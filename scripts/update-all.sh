#!/usr/bin/env bash
# Update the GenomeFlow source, all Conda packages in its environment,
# ABRicate databases, MOB-suite reference data and optional Bakta database.
# Run from Linux/macOS/WSL2, NEVER native Windows PowerShell.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_NAME="genomeflow"
CONFIRM=0
BAKTA_DB_PATH=""

usage() {
  cat <<'HELP'
GenomeFlow environment/database updater (Linux, macOS, WSL2)
Usage: bash scripts/update-all.sh [--yes] [--bakta-db /absolute/path]
  --yes                Accept the explicit update prompt (non-interactive)
  --bakta-db PATH      Also update an existing optional Bakta DB at PATH
  -h, --help           Show this message

Updates the entire Conda environment, default ABRicate databases, and
MOB-suite DB. This may take a long time and download >1 GB.
Keep previous research results and version snapshots for reproducibility.
HELP
}

while (($#)); do
  case "$1" in
    --yes) CONFIRM=1; shift ;;
    --bakta-db)
      if (($# < 2)); then echo "Missing value for --bakta-db" >&2; exit 2; fi
      BAKTA_DB_PATH="$2"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage >&2; exit 2 ;;
  esac
done

for binary in git conda mamba; do
  command -v "$binary" >/dev/null 2>&1 || {
    echo "Missing command: $binary. Activate/initialize Miniforge before updating." >&2
    exit 127
  }
done
[[ -d "$ROOT/.git" ]] || { echo "Not a Git clone: $ROOT" >&2; exit 2; }
[[ -z "$(git -C "$ROOT" status --porcelain)" ]] || {
  echo "Local changes found; commit or stash before updating (git status)." >&2
  exit 2
}
git -C "$ROOT" remote get-url origin >/dev/null || {
  echo "No GitHub 'origin' remote configured." >&2
  exit 2
}

if (( !CONFIRM )); then
  echo "This updates ALL packages in Conda env '$ENV_NAME' plus reference databases."
  echo "It may change scientific results and download large files."
  read -r -p "Continue? Type UPDATE: " answer
  [[ "$answer" == UPDATE ]] || { echo "Cancelled."; exit 1; }
fi

snapshot_dir="$HOME/.local/share/genomeflow/update-snapshots/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$snapshot_dir"
echo "Version snapshots: $snapshot_dir"
conda list -n "$ENV_NAME" --explicit > "$snapshot_dir/conda-before-explicit.txt"
conda env export -n "$ENV_NAME" > "$snapshot_dir/environment-before.yaml"
git -C "$ROOT" rev-parse HEAD > "$snapshot_dir/genomeflow-commit-before.txt"

prefix="$(conda run -n "$ENV_NAME" python -c 'import sys; print(sys.prefix)' | tail -n 1)"
[[ -d "$prefix/conda-meta" ]] || { echo "Environment not found: $prefix" >&2; exit 2; }

pinfile="$prefix/conda-meta/pinned"
had_pins=0
if [[ -e "$pinfile" ]]; then
  had_pins=1
  cp -p "$pinfile" "$snapshot_dir/pinned-original"
fi
restore_pins() {
  if ((had_pins)); then
    cp -p "$snapshot_dir/pinned-original" "$pinfile"
  else
    rm -f "$pinfile"
  fi
}
trap restore_pins EXIT

# Temporary compatibility pins; never modify the base environment.
printf '\npython 3.11.*\nsnakemake >=8,<10\n' >> "$pinfile"

echo "1/6 Updating GenomeFlow source (fast-forward only)..."
git -C "$ROOT" pull --ff-only

echo "2/6 Updating all Conda packages while retaining Python 3.11 and Snakemake <10..."
mamba update -y -n "$ENV_NAME" -c conda-forge -c bioconda --all

echo "3/6 Revalidating required packages and reinstalling editable GenomeFlow..."
mamba install -y -n "$ENV_NAME" -c conda-forge -c bioconda \
  'python=3.11' 'snakemake>=8,<10' prokka abricate mob_suite typer pyyaml pip pytest
conda run -n "$ENV_NAME" python -m pip install --no-deps -e "$ROOT"

echo "4/6 Refreshing all three GenomeFlow default ABRicate reference databases..."
for db in resfinder vfdb plasmidfinder; do
  echo "Updating ABRicate database: $db"
  conda run -n "$ENV_NAME" abricate-get_db --db "$db" --force
done
conda run -n "$ENV_NAME" abricate --setupdb
conda run -n "$ENV_NAME" abricate --list | tee "$snapshot_dir/abricate-databases-after.tsv"

echo "5/6 Reinitializing MOB-suite database (large download; do not interrupt)..."
conda run -n "$ENV_NAME" mob_init

if [[ -n "$BAKTA_DB_PATH" ]]; then
  [[ -d "$BAKTA_DB_PATH" ]] || { echo "Bakta database path not found: $BAKTA_DB_PATH" >&2; exit 2; }
  [[ -x "$prefix/bin/bakta_db" ]] || {
    echo "Bakta not installed in '$ENV_NAME'. Install it before using --bakta-db." >&2
    exit 2
  }
  echo "Updating optional Bakta database: $BAKTA_DB_PATH"
  conda run -n "$ENV_NAME" bakta_db update --db "$BAKTA_DB_PATH"
else
  echo "Optional Bakta DB not changed (not the default annotator). To update it, pass --bakta-db PATH."
fi

echo "6/6 Verifying environment and running unit tests..."
conda run -n "$ENV_NAME" genomeflow --help >/dev/null
(
  cd "$ROOT"
  conda run -n "$ENV_NAME" python -m pytest -q
)
conda list -n "$ENV_NAME" --explicit > "$snapshot_dir/conda-after-explicit.txt"
conda env export -n "$ENV_NAME" > "$snapshot_dir/environment-after.yaml"
git -C "$ROOT" rev-parse HEAD > "$snapshot_dir/genomeflow-commit-after.txt"
echo "Update complete. Snapshots stored in: $snapshot_dir"
echo "IMPORTANT: for a comparative study, retain prior versions or rerun the cohort consistently."
