# Installing GenomeFlow v0.2

GenomeFlow processes **assembled bacterial FASTA files**, using external Snakemake, Prokka (or optionally Bakta), ABRicate and MOB-suite tools. **Research prototype:** Mac and Windows/WSL2 routes are experimental and not yet tested end to end.

Choose a platform-specific step-by-step guide:

- [Debian / Ubuntu](docs/install-debian.md) — recommended Linux route.
- [macOS Intel / Apple Silicon](docs/install-macos.md) — experimental; native dependency resolution may vary.
- [Windows PowerShell + Ubuntu/WSL2](docs/install-windows-powershell.md) — PowerShell calls Linux tools in WSL2; **not a native Windows port**.

## Linux quick installation (Miniforge already installed)

```bash
git clone https://github.com/afsansarwer/genomeflow.git
cd genomeflow
source "$HOME/miniforge3/etc/profile.d/conda.sh"
mamba create -y -n genomeflow -c conda-forge -c bioconda \
  python=3.11 snakemake prokka abricate mob_suite typer pyyaml pip pytest
conda activate genomeflow
python -m pip install --no-deps -e .
genomeflow --help
abricate --list
```

If Miniforge is missing, install it using the selected OS-specific guide. The ABRicate databases `resfinder`, `vfdb` and `plasmidfinder` should be available; MOB-suite may need a first-time database download.

## One-command analysis

```bash
genomeflow genome.fna -o results/ -t 4
genomeflow genomes/ -o batch_results/ -t 8
```

These inputs must be assembled nucleotide FASTAs rather than raw FASTQ reads. Avoid placing source FASTAs inside the output folder. The bundled tiny synthetic example is for input/QC testing, **not complete biological validation**.

## Keeping GenomeFlow and its reference databases up to date

Run `bash scripts/update-all.sh` from a clean Git clone in a Linux/macOS/WSL2 terminal, after initializing Miniforge. See [the full update guide](docs/updating.md) for snapshots, reference database refreshes, and reproducibility precautions. The update is **not** an automatic or transactional rollback.

## For advanced users

```bash
genomeflow init project
cp genome.fna project/genomes/
cd project
genomeflow doctor --config config.yaml
genomeflow run --config config.yaml --cores 4
```

For more options see [command reference](command_help.md), [troubleshooting](docs/troubleshooting.md), and [validation limits](docs/validation.md). Keep your Conda `base` environment untouched.
