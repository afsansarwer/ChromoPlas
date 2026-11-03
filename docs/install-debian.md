# Debian / Ubuntu installation

Use this guide to install ChromoPlas on Debian or Ubuntu (x86_64). You will need internet access and storage for MOB-suite reference data.

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
mamba create -y -n chromoplas -c conda-forge -c bioconda \
  python=3.11 snakemake abricate mob_suite typer pyyaml pip pytest
conda activate chromoplas
python -m pip install --no-deps -e .
~~~

The **--no-deps** option assumes all dependencies were installed by Mamba; do not run this installation in the Conda base environment.

## 4. Check the setup

~~~bash
which python chromoplas snakemake abricate mob_recon
chromoplas --help
abricate --list
~~~

The default workflow expects ABRicate reference databases named **resfinder**, **vfdb**, and **plasmidfinder**. MOB-suite may need a large first-time reference database download. See [Troubleshooting](troubleshooting.md).

## 5. Run on assembled bacterial genomes

~~~bash
chromoplas /path/to/genome.fna -o "$HOME/chromoplas-results" -t 4
chromoplas /path/to/genomes/ -o "$HOME/chromoplas-batch" -t 8
xdg-open "$HOME/chromoplas-results/07_reports/report.html"
~~~

Use a real assembled bacterial genome and keep input files outside the output directory.

### Update later

See [update-all instructions](updating.md). This refreshes tools and databases rather than just repository code.

See [command reference](../command_help.md) and [validation limitations](validation.md).
