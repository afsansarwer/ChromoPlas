# Install ChromoPlas v0.3 (development)

ChromoPlas runs on assembled bacterial FASTA input. It needs Snakemake, ABRicate and MOB-suite in a Linux environment with initialized databases. macOS native installs are experimental; on Windows use Ubuntu in WSL2.

## Debian or Ubuntu

~~~bash
sudo apt update
sudo apt install -y git curl ca-certificates
curl -fsSLo Miniforge3.sh "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-$(uname -m).sh"
bash Miniforge3.sh -b -p "$HOME/miniforge3"
source "$HOME/miniforge3/etc/profile.d/conda.sh"
git clone https://github.com/afsansarwer/genomeflow.git
cd genomeflow
git switch chromoplas-v0.3-core
mamba create -y -n chromoplas -c conda-forge -c bioconda python=3.11 'snakemake>=8,<10' abricate mob_suite typer pyyaml pip pytest
conda activate chromoplas
python -m pip install --no-deps -e .
chromoplas doctor
~~~

After the development branch is merged, the git switch command is unnecessary.

## macOS

Use the same installation sequence, replacing the Miniforge download with Miniforge3-MacOSX-$(uname -m).sh. ARM64 package availability may be limited. Native macOS end-to-end testing is pending.

## Windows PowerShell

Install Ubuntu via WSL2 from elevated PowerShell with wsl --install -d Ubuntu. Run the Debian/Ubuntu instructions INSIDE Ubuntu. This does not install a native Windows version.

## Databases

Check abricate --list for resfinder, vfdb and plasmidfinder. MOB-suite requires its own initialized reference database, often downloaded during package post-link initialization.

## Quick run

~~~bash
chromoplas isolate.fna -o results -t 4
chromoplas assemblies/ -o results_batch -t 8
chromoplas isolate.fna -o results --dry-run
~~~

Use a new output directory for independent projects. The first dry-run can show a partial DAG because HQ selection is a Snakemake checkpoint.

Prokka is optional, and must be installed separately if enabled in YAML. CheckM2 and Bakta are not integrated into the v0.3 development candidate. See command_help.md, docs/architecture.md, docs/validation.md and docs/updating.md.
