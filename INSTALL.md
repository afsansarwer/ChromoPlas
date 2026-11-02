# GenomeFlow installation (Linux)

GenomeFlow v0.2 is a research prototype for assembled bacterial genomes.

## Prerequisites

- Linux x86_64; Miniforge/Mamba recommended.
- Internet access for MOB-suite reference database initialization.
- At least 8 GB RAM for small tests; more for batch workloads.
- Local assembled FASTA (`.fna`, `.fa`, `.fasta`, optionally gzip-compressed).

## Clone and install

```bash
git clone https://github.com/OWNER/genomeflow.git
cd genomeflow
eval "$(mamba shell hook --shell bash)"   # for Bash, current session
mamba create -y -n genomeflow -c conda-forge -c bioconda \
  python=3.11 snakemake prokka abricate mob_suite typer pyyaml pip pytest
mamba activate genomeflow
python -m pip install --no-deps -e .
genomeflow --help
```

Replace `OWNER` with the GitHub username once the repository is published.
For Zsh use `eval "$(mamba shell hook --shell zsh)"`.

## Prepare reference databases

MOB-suite normally initializes its database during installation; first-time setup may download hundreds of MB.
Verify the command works with `mob_recon --help`.
Inspect ABRicate databases:

```bash
abricate --list
```

If required databases are absent or stale, consult ABRicate documentation for `abricate-get_db --db NAME` and `abricate --setupdb`.

## One-command analysis

```bash
genomeflow isolate.fna -o results/ -t 4
genomeflow genomes/ -o batch_results/ -t 8
```

To preview, append `--dry-run`. A fresh output directory is recommended for each independent dataset.
The first dry run can show only checkpoint-related jobs because Snakemake expands the downstream DAG after quality selection.

## Advanced mode

```bash
genomeflow init project
cp isolate.fna project/genomes/
cd project
genomeflow doctor --config config.yaml
genomeflow run --config config.yaml --cores 4
```

## Tests

```bash
python -m pytest -q
python -m compileall -q src
```

## Notes and limitations

- The QC filter uses FASTA assembly metrics; it does NOT estimate contamination or completeness.
- Plasmid reconstruction is computational prediction, not experimental confirmation.
- ABRicate calls depend on selected databases and thresholds.
- Validate outputs against trusted reference genomes before publication.
- Do not run `pip install -e .` in your Conda base environment; activate the target environment first.
