# GenomeFlow v0.2 — Command Help

A quick-reference guide for analyzing assembled bacterial genomes with GenomeFlow on Linux.

## 1. Activate the environment

```bash
# For Bash, if `mamba activate` says the shell is not initialized:
eval "$(mamba shell hook --shell bash)"
mamba activate genomeflow
```

Check that the CLI and dependencies are available:

```bash
which genomeflow
python --version
genomeflow --help
snakemake --version
```

## 2. Install from a local clone

From the repository root (the folder containing `pyproject.toml`):

```bash
python -m pip install --no-deps -e .
```

This assumes the `genomeflow` environment already contains Snakemake, Typer, PyYAML, Prokka, ABRicate, and MOB-suite. `--no-deps` does **not** install missing dependencies.

For a normal non-editable installation, use `python -m pip install --no-deps .`.

## 3. Simple commands (recommended)

```bash
# Single genome
genomeflow genome.fasta -o results/

# Another accepted FASTA extension
genomeflow genome.fna -o results/

# All FASTA assemblies in a folder
genomeflow genomes/ -o results/ -t 8

# Several genomes
genomeflow sample1.fna sample2.fasta -o results/ -t 4

# Preview without executing
genomeflow genome.fasta -o results/ --dry-run

# Optional advanced settings
genomeflow genome.fasta -o results/ --config custom.yaml

# Continue a previous run: repeat the same command and output directory
genomeflow genome.fasta -o results/ -t 4
```

**Important:** `--resume` and `--strict` are **not** implemented flags in v0.2. Repeating a run in the same output directory uses Snakemake's normal resume behavior. A custom YAML file is needed to change QC thresholds.

### Simple CLI options

| Option | Meaning |
| --- | --- |
| `-o`, `--output` | Required output directory |
| `-t`, `--threads` | Number of Snakemake cores (default: 4) |
| `-c`, `--config` | Optional YAML configuration |
| `--dry-run` | Show planned steps without executing |
| `--keep-going` | Continue independent jobs after a job fails |
| `--help` | Display command help |

For help with the simplified interface, run `genomeflow analyze --help`.

## 4. Advanced / project-based commands

```bash
# Create project with config.yaml and genomes/ folder
genomeflow init my_project
cd my_project

# Put FASTA files into genomes/ before running doctor or qc
# Check tool locations and number of input FASTAs
genomeflow doctor --config config.yaml

# Run FASTA-derived assembly QC and HQ filtering
genomeflow qc --config config.yaml

# Full Snakemake pipeline
genomeflow run --config config.yaml --cores 4

# Preview full pipeline
genomeflow run --config config.yaml --cores 4 --dry-run

# Keep processing independent jobs if one fails
genomeflow run --config config.yaml --cores 4 --keep-going
```

**Note:** In v0.2, `genomeflow doctor` requires a config file and at least one recognized FASTA in the configured folder. It checks executable paths but does not fully verify external database readiness.

## 5. Accepted input files

- `.fasta`, `.fa`, `.fna`
- `.fasta.gz`, `.fa.gz`, `.fna.gz`
- A directory containing FASTA files, or multiple FASTA paths

Each sample must have a distinct filename when staged together. Do not put input files inside the output directory. Avoid reusing one output directory for unrelated datasets.

## 6. Main output folders

```text
results/
├── 00_metadata/           # Resolved config, sample manifest, input links
├── 02_quality/            # QC metrics, pass/fail selection
├── 03_annotation/         # Prokka/Bakta annotation outputs
├── 04_abricate/           # Whole-genome ResFinder, VFDB, PlasmidFinder
├── 05_plasmids/           # MOB-suite reconstruction outputs
├── 06_plasmid_abricate/   # ABRicate screening of predicted plasmids
└── 07_reports/
    └── report.html        # Final HTML report
```

Open the report in your browser:

```bash
xdg-open results/07_reports/report.html
```

## 7. Troubleshooting

**`mamba activate` says shell not initialized**

```bash
eval "$(mamba shell hook --shell bash)"
mamba activate genomeflow
```

**`ModuleNotFoundError: No module named 'typer'`**

```bash
mamba install -n genomeflow -c conda-forge typer pyyaml
```

**`No FASTA files found`** — Check that the input path exists and contains a recognized FASTA extension.

**Tool not found** — Check the active environment and executable paths:

```bash
which python genomeflow snakemake prokka abricate mob_recon
```

**Workflow interrupted** — Correct the cause, then rerun the same GenomeFlow command using the same output directory. Preserve `.snakemake/` and intermediate files.

**Database errors** — Confirm ABRicate databases and MOB-suite reference databases are initialized; consult the upstream tool documentation.

## 8. Scientific cautions

- v0.2 quality selection uses assembly FASTA metrics, **not** CheckM2 completeness or contamination.
- MOB-suite plasmids are computational predictions; they are not necessarily complete circular plasmids.
- Record database versions, parameters, and accession metadata for reproducibility.
- This release is an early prototype. Validate biological results against known genomes before using them in a manuscript.
