#!/usr/bin/env bash
# ChromoPlas installer for Debian/Ubuntu and Ubuntu/WSL2.
# Run from Bash OR Zsh with: bash INSTALL.sh
set -Eeuo pipefail

REPO_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ENV_NAME="chromoplas"

info() { printf '\n[ChromoPlas] %s\n' "$*"; }
fail() { printf '\n[ChromoPlas] ERROR: %s\n' "$*" >&2; exit 1; }
trap 'printf "\n[ChromoPlas] Installation stopped at line %s. No success claimed.\n" "$LINENO" >&2' ERR

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
  cat <<'HELP'
Usage: bash INSTALL.sh

Installs ChromoPlas and its dependencies into a dedicated Conda environment
named chromoplas. Uses an existing Miniconda/Miniforge/Anaconda installation,
or installs Miniforge into ~/miniforge3 if Conda is not found.
Supported: Debian/Ubuntu x86_64 Linux, including Ubuntu under WSL2.
Requires an internet connection and free disk space for tools and databases.
The script never installs ChromoPlas into the Conda base environment.
HELP
  exit 0
fi
[[ $# -eq 0 ]] || fail "Unknown option: $1 (try --help)"
[[ -f "$REPO_DIR/pyproject.toml" ]] || fail "Run the INSTALL.sh included in your ChromoPlas clone."
[[ "$(uname -s)" == "Linux" ]] || fail "This installer targets Debian/Ubuntu Linux and WSL2. See INSTALL.md for other systems."
[[ "$(uname -m)" == "x86_64" ]] || fail "This installer is tested for Linux x86_64 only. See platform guides for other architectures."
if [[ -r /etc/os-release ]]; then
  . /etc/os-release
  case " ${ID:-} ${ID_LIKE:-} " in
    *" debian "*|*" ubuntu "*) ;;
    *) fail "This guided installer supports Debian/Ubuntu (including WSL2). See INSTALL.md for other Linux distributions." ;;
  esac
fi

info "Setting up a dedicated Conda environment, not (base)."
CONDA_BIN=""
if [[ -n "${CONDA_EXE:-}" && -x "${CONDA_EXE}" ]]; then
  CONDA_BIN="$CONDA_EXE"
elif command -v conda >/dev/null 2>&1; then
  CONDA_BIN="$(command -v conda)"
else
  for candidate in "$HOME/miniconda3/bin/conda" "$HOME/miniforge3/bin/conda" "$HOME/anaconda3/bin/conda"; do
    if [[ -x "$candidate" ]]; then CONDA_BIN="$candidate"; break; fi
  done
fi

if [[ -z "$CONDA_BIN" ]]; then
  info "Conda not found; installing official Miniforge under ~/miniforge3."
  if ! command -v curl >/dev/null 2>&1 || ! command -v sha256sum >/dev/null 2>&1; then
    if ! command -v apt-get >/dev/null 2>&1; then
      fail "Install curl, coreutils and CA certificates first."
    fi
    info "Installing download prerequisites with apt. A sudo password may be required."
    if [[ "$(id -u)" == "0" ]]; then
      apt-get update
      apt-get install -y curl ca-certificates coreutils
    else
      command -v sudo >/dev/null 2>&1 || fail "sudo is required for apt prerequisites."
      sudo apt-get update
      sudo apt-get install -y curl ca-certificates coreutils
    fi
  fi
  [[ ! -e "$HOME/miniforge3" ]] || fail "~/miniforge3 exists but Conda is missing; inspect this directory before rerunning."
  tmp_dir="$(mktemp -d)"
  trap 'rm -rf -- "${tmp_dir:-}"' EXIT
  installer="Miniforge3-Linux-$(uname -m).sh"
  url="https://github.com/conda-forge/miniforge/releases/latest/download/$installer"
  curl --fail --location --retry 3 --output "$tmp_dir/$installer" "$url"
  curl --fail --location --retry 3 --output "$tmp_dir/$installer.sha256" "$url.sha256"
  (cd "$tmp_dir" && sha256sum --check "$installer.sha256") || fail "Miniforge installer checksum failed."
  bash "$tmp_dir/$installer" -b -p "$HOME/miniforge3"
  CONDA_BIN="$HOME/miniforge3/bin/conda"
fi

[[ -x "$CONDA_BIN" ]] || fail "Conda executable not available: $CONDA_BIN"
CONDA_BASE="$("$CONDA_BIN" info --base)"
[[ -d "$CONDA_BASE" ]] || fail "Cannot find Conda base path."
info "Using Conda: $CONDA_BIN"

# Conda runs via its executable, never within the user's (base) Python.
# Activation in a parent Zsh/Bash shell is not required for installation.
packages=(python=3.11 'snakemake>=8,<10' abricate mob_suite typer pyyaml pip pytest)
if "$CONDA_BIN" env list | awk '$1 == "chromoplas" { found=1 } END { exit !found }'; then
  info "Environment chromoplas already exists; ensuring its dependencies are installed."
  "$CONDA_BIN" install -y -n "$ENV_NAME" --override-channels -c conda-forge -c bioconda "${packages[@]}"
else
  info "Creating Conda environment chromoplas (this can take time on first install)."
  "$CONDA_BIN" create -y -n "$ENV_NAME" --override-channels -c conda-forge -c bioconda "${packages[@]}"
fi

info "Installing ChromoPlas into chromoplas (never base)."
"$CONDA_BIN" run --no-capture-output -n "$ENV_NAME" python -m pip install --no-deps -e "$REPO_DIR"

info "Checking ABRicate databases (ResFinder, VFDB, PlasmidFinder)."
if ! "$CONDA_BIN" run -n "$ENV_NAME" abricate --list | awk '
  tolower($1)=="resfinder" {a=1}
  tolower($1)=="vfdb" {b=1}
  tolower($1)=="plasmidfinder" {c=1}
  END {exit !(a && b && c)}
'; then
  info "Required ABRicate databases were not found; initializing bundled databases."
  "$CONDA_BIN" run --no-capture-output -n "$ENV_NAME" abricate --setupdb
fi

info "Checking MOB-suite reference database."
if ! "$CONDA_BIN" run -n "$ENV_NAME" python -c '
from pathlib import Path
from mob_suite.constants import default_database_dir
p=Path(default_database_dir)
assert (p / "status.txt").is_file() and (p / "ncbi_plasmid_full_seqs.fas.msh").is_file()
' >/dev/null 2>&1; then
  info "Initializing MOB-suite reference database (large download; needs internet)."
  "$CONDA_BIN" run --no-capture-output -n "$ENV_NAME" mob_init
fi

info "Running required installation checks."
"$CONDA_BIN" run --no-capture-output -n "$ENV_NAME" chromoplas doctor
"$CONDA_BIN" run --no-capture-output -n "$ENV_NAME" bash "$REPO_DIR/scripts/check-install.sh"

info "Installation finished successfully!"
printf '\nNext commands in your WSL/Linux terminal:\n'
printf '  conda activate chromoplas\n'
printf '  chromoplas --help\n'
printf '  chromoplas doctor\n'
printf '  chromoplas ~/genomes/genome.fna -o ~/chromoplas-results -t 4\n'
printf '\nUse your own assembled FASTA for the final command.\n'
printf 'If conda activate is not available in your current shell, run:\n'
printf '  source "%s/etc/profile.d/conda.sh"\n' "$CONDA_BASE"
printf '  conda activate chromoplas\n'
