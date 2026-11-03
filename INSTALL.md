# ChromoPlas installation

**Start here:** ChromoPlas uses Python 3.11, Snakemake, ABRicate, MOB-suite and the ResFinder/VFDB/PlasmidFinder databases. Install these together in a dedicated Miniforge/Mamba environment; do not install them into the base environment.

| Operating system | Guide |
| --- | --- |
| **Omarchy / Arch Linux** | [Omarchy: Bash hashing + Conda/Mamba activation](docs/install-omarchy.md) |
| **Debian / Ubuntu** | [Linux installation](docs/install-debian.md) |
| **macOS (Intel / Apple Silicon)** | [macOS installation](docs/install-macos.md) |
| **Windows PowerShell** | [Ubuntu/WSL2 installation + launcher](docs/install-windows-powershell.md) |

## Install using an existing Miniforge installation (Linux)

Run in **Bash**. On Omarchy, initialize Bash hashing first with **set -h** (see the guide above).

~~~bash
set -h
source "$HOME/miniforge3/etc/profile.d/conda.sh"

git clone https://github.com/afsansarwer/genomeflow.git
cd genomeflow

mamba create -y -n chromoplas -c conda-forge -c bioconda \
  python=3.11 'snakemake>=8,<10' abricate mob_suite typer pyyaml pip pytest

conda activate chromoplas
python -m pip install --no-deps -e .
~~~

If the repository is already cloned, skip the git clone command, enter that repository's directory and run **git pull --ff-only** before installation. If the chromoplas environment already exists, **do not recreate it**: activate it and run the editable pip installation.

## Verify the installation

~~~bash
echo "$CONDA_DEFAULT_ENV"           # chromoplas
command -v chromoplas
command -v snakemake
command -v abricate
command -v mob_recon
chromoplas --help
abricate --list
chromoplas doctor
~~~

Check that ABRicate lists **resfinder**, **vfdb**, and **plasmidfinder**, and that MOB-suite's reference data are available. The doctor command checks executables and the ABRicate database list; an actual analysis verifies the remaining tool/database compatibility.

**Omarchy activation error?** If Bash prints *hash: hashing disabled*, follow the [permanent Omarchy shell fix](docs/install-omarchy.md). If the environment activates but chromoplas is missing, run the Python package installation command from the repository root.

## Run

~~~bash
chromoplas isolate.fna -o results/ -t 4
chromoplas assemblies/ -o batch_results/ -t 8
~~~

View **results/07_reports/report.html** after the workflow completes. Supply assembled bacterial FASTAs, not raw FASTQ reads; keep inputs outside the chosen output directory.

## Optional and maintenance commands

~~~bash
# Optional Prokka annotation tool (only if needed for a custom YAML run)
mamba install -n chromoplas -c conda-forge -c bioconda prokka

# Run unit tests from the repository root
python -m pytest -q
~~~

Prokka annotation is disabled by default to reduce runtime. For database and tool updates, follow [Updating ChromoPlas](docs/updating.md). For commands, see [Command reference](command_help.md).

**Project status:** ChromoPlas v0.3.0; the Python tests and workflow dry-run have passed in CI. Cross-platform and biological end-to-end validation continues.
