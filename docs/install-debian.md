# Debian / Ubuntu installation

**Recommended Linux route (experimental on individual distributions).** GenomeFlow has completed an end-to-end run on Linux, but not every Debian or Ubuntu release has been validated. Use an x86_64 system, internet access, and enough storage for MOB-suite reference data.

## 1. System prerequisites

Open a Bash terminal:

~~~bash
sudo apt update
sudo apt install -y git curl ca-certificates
~~~

## 2. Install Miniforge

If you already installed Miniforge, skip the installer and use the existing Conda installation.

~~~bash
curl -fsSLo Miniforge3.sh "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-$(uname -m).sh"
bash Miniforge3.sh -b -p "$HOME/miniforge3"
source "$HOME/miniforge3/etc/profile.d/conda.sh"
~~~

You can run **conda init bash** and restart Bash to enable automatic initialization in future terminals.

## 3. Clone and install

~~~bash
git clone https://github.com/afsansarwer/genomeflow.git
cd genomeflow
mamba create -y -n genomeflow -c conda-forge -c bioconda \
  python=3.11 snakemake prokka abricate mob_suite typer pyyaml pip pytest
conda activate genomeflow
python -m pip install --no-deps -e .
~~~

The **--no-deps** option assumes all dependencies were installed by Mamba; do not run this installation in the Conda base environment.

## 4. Check the setup

~~~bash
which python genomeflow snakemake prokka abricate mob_recon
genomeflow --help
abricate --list
~~~

The default workflow expects ABRicate reference databases named **resfinder**, **vfdb**, and **plasmidfinder**. MOB-suite may need a large first-time reference database download. See [Troubleshooting](troubleshooting.md).

## 5. Run on assembled bacterial genomes

~~~bash
genomeflow /path/to/genome.fna -o "$HOME/genomeflow-results" -t 4
genomeflow /path/to/genomes/ -o "$HOME/genomeflow-batch" -t 8
xdg-open "$HOME/genomeflow-results/07_reports/report.html"
~~~

The bundled tiny synthetic FASTA is for CLI/QC checks, **not** a meaningful full biological test. Use a real assembled bacterial genome. Do not place inputs inside the output folder.

### Update later

~~~bash
cd genomeflow
git pull --ff-only
conda activate genomeflow
python -m pip install --no-deps -e .
~~~

See [command reference](../command_help.md) and [validation limitations](validation.md).
