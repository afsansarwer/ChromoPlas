# GenomeFlow command reference (v0.2)

GenomeFlow accepts **assembled bacterial genome FASTA** files or folders, not raw sequencing reads.

### Installation

- [Debian / Ubuntu](docs/install-debian.md)
- [macOS (Intel and Apple Silicon)](docs/install-macos.md)
- [Windows PowerShell + WSL2](docs/install-windows-powershell.md)
- [General installation overview](INSTALL.md)

### Linux and macOS commands

```bash
# One assembly
genomeflow genome.fna -o results/ -t 4

# Folder of assemblies
genomeflow genomes/ -o batch_results/ -t 8

# Multiple assemblies
genomeflow sample1.fna sample2.fasta -o results/ -t 4

# Check dependency graph (the QC checkpoint can delay downstream expansion)
genomeflow genome.fna -o results/ --dry-run

# Custom thresholds/settings
genomeflow genome.fna -o results/ --config custom.yaml

# Resume an interrupted run using identical input and output path
genomeflow genome.fna -o results/ -t 4

# Help
genomeflow --help
genomeflow analyze --help
```

| Option | Function |
| --- | --- |
| `-o, --output` | Output directory (required) |
| `-t, --threads` | Snakemake cores (default 4) |
| `-c, --config` | Optional YAML configuration |
| `--dry-run` | Preview planned jobs |
| `--keep-going` | Continue unrelated jobs after a failure |

**Not implemented in v0.2:** `--strict` and `--resume` flags. Rerunning the same command usually lets Snakemake resume without special flags.

### Windows PowerShell (Ubuntu/WSL2 required)

The PowerShell launcher is an **experimental wrapper for the Linux installation**, not a native Windows genome-analysis implementation. First install GenomeFlow in Ubuntu/WSL2 using the [Windows guide](docs/install-windows-powershell.md).

```powershell
.\scripts\GenomeFlow.ps1 -InputPath "C:\Users\YOU\Downloads\genome.fna" -OutputPath "C:\Users\YOU\GenomeFlow-results" -Threads 4

# Preview
.\scripts\GenomeFlow.ps1 -InputPath "C:\Users\YOU\Genomes" -OutputPath "C:\Users\YOU\GenomeFlow-batch" -Threads 4 -DryRun
```

Supported input extensions: `.fna`, `.fasta`, `.fa`, with optional `.gz`. Avoid duplicate filenames and keep input FASTAs outside the output directory.

### Updating GenomeFlow and databases

From the repository's root folder in Linux/macOS/WSL2:

```bash
source "$HOME/miniforge3/etc/profile.d/conda.sh"
conda activate base
bash scripts/update-all.sh
```

The updater refreshes the compatible Conda environment, default ABRicate databases and MOB-suite references; optional Bakta databases require `--bakta-db PATH`. See [full update instructions](docs/updating.md), including snapshots and scientific reproducibility warnings.

### Advanced project workflow

```bash
genomeflow init my_project
cp genome.fna my_project/genomes/
cd my_project
genomeflow doctor --config config.yaml
genomeflow qc --config config.yaml
genomeflow run --config config.yaml --cores 4
```

The current `doctor` command checks executable paths and FASTA count, not complete database readiness.

### Output

`results/02_quality/quality_summary.tsv`: FASTA QC metrics and selection. `03_annotation/`: Prokka or Bakta. `04_abricate/`: genome screening. `05_plasmids/`: MOB-suite predictions. `06_plasmid_abricate/`: plasmid screening. `07_reports/report.html`, `master_summary.tsv`, and `all_abricate_hits.tsv`: reports.

### Scientific considerations

Threshold-based assembly QC is **not** contamination/completeness testing; ABRicate gene calls depend on reference databases; inferred plasmids are not experimentally verified. See [validation and reproducibility](docs/validation.md) and [troubleshooting](docs/troubleshooting.md).
