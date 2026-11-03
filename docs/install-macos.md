# macOS installation (Intel and Apple Silicon)

**Experimental:** No full ChromoPlas v0.3 run has yet been validated on macOS. The Python interface is portable, but ABRicate, MOB-suite and their dependent packages may vary by architecture. Package resolution is not guaranteed, especially on Apple Silicon.

## 1. Identify your architecture

Open macOS Terminal:

~~~bash
uname -m
~~~

**x86_64** means Intel; **arm64** means Apple Silicon. If Git or build tools are missing, install Apple's command-line tools using **xcode-select --install**.

## 2. Install Miniforge

If Miniforge already exists, skip downloading it and initialize your existing installation.

~~~bash
curl -fsSLo Miniforge3.sh "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-MacOSX-$(uname -m).sh"
bash Miniforge3.sh -b -p "$HOME/miniforge3"
source "$HOME/miniforge3/etc/profile.d/conda.sh"
~~~

macOS usually uses **zsh**. You may optionally run **conda init zsh** and open a new Terminal.

## 3. Clone and install

~~~bash
git clone https://github.com/afsansarwer/genomeflow.git
cd genomeflow
mamba create -y -n chromoplas -c conda-forge -c bioconda \
  python=3.11 snakemake abricate mob_suite typer pyyaml pip pytest
conda activate chromoplas
python -m pip install --no-deps -e .
~~~

**If Mamba reports unsatisfiable dependencies**, stop and record the exact error and architecture. Do not replace unavailable native bioinformatics tools with unrelated pip wheels. On Apple Silicon, an x86_64/Rosetta environment or Linux virtual machine may be an alternative, but those fallbacks have **not** been tested for ChromoPlas.

## 4. Verify

~~~bash
chromoplas --help
which snakemake abricate mob_recon
abricate --list
~~~

Check that the default ABRicate databases are installed and MOB-suite's database initialized successfully.

## 5. Run

~~~bash
chromoplas "$HOME/Downloads/genome.fna" -o "$HOME/chromoplas-results" -t 4
open "$HOME/chromoplas-results/07_reports/report.html"
~~~

Replace the sample path with a real **assembled** genome. Try a single well-characterized isolate and validate its biological results before batch analysis.

See [update-all instructions](updating.md), [Troubleshooting](troubleshooting.md), [command reference](../command_help.md), [validation notes](validation.md), and [Miniforge](https://github.com/conda-forge/miniforge).
