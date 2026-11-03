# ChromoPlas: beginner's guide

ChromoPlas turns an **assembled bacterial genome FASTA** into a chromosome/plasmid gene-localization map and a browser report. You do not need to know Python or Snakemake to run it.

## 1. Understand the installation

- **Miniforge** provides Conda/Mamba (software environment managers).
- **The `chromoplas` Conda environment** contains Python, Snakemake, ABRicate, MOB-suite and dependencies.
- **The ChromoPlas package** supplies the `chromoplas` command. It must be installed separately inside that environment.

## 2. Activate the environment

**Omarchy / Arch Linux (Bash):**

```bash
set -h
source "$HOME/miniforge3/etc/profile.d/conda.sh"
conda activate chromoplas
```

To make activation permanent, use the [Omarchy guide](install-omarchy.md). The `set -h` line addresses Omarchy's `hash: hashing disabled` conflict.

**Debian / Ubuntu (Bash):**

```bash
source "$HOME/miniforge3/etc/profile.d/conda.sh"
conda activate chromoplas
```

**macOS (Zsh):**

```zsh
source "$HOME/miniforge3/etc/profile.d/conda.sh"
conda activate chromoplas
```

**Windows:** Open Ubuntu/WSL2 and run the Debian/Ubuntu commands there. See [Windows setup](install-windows-powershell.md).

## 3. Check everything

```bash
echo "$CONDA_DEFAULT_ENV"  # expected: chromoplas
command -v python
command -v chromoplas
chromoplas --help
chromoplas doctor
```

If the environment activates but `chromoplas` is missing, navigate to your cloned repository (the directory containing `pyproject.toml`):

```bash
cd ~/genomeflow  # or your actual clone directory
git pull --ff-only
python -m pip install --no-deps -e .
bash scripts/check-install.sh
```

If the Conda environment does not exist, see [installation](../INSTALL.md) before these steps.

## 4. Analyze a single genome

```bash
chromoplas ~/Downloads/isolate.fna -o ~/chromoplas-results -t 4
```

- `~/Downloads/isolate.fna` is the **input assembled bacterial genome**, not FASTQ reads.
- `-o ~/chromoplas-results` selects the results folder.
- `-t 4` allocates four total Snakemake cores.

For many assembled genomes, process each independently:

```bash
chromoplas ~/assemblies/ -o ~/chromoplas-batch -t 8
```

## 5. Open the report

```bash
# Linux
xdg-open ~/chromoplas-results/07_reports/report.html

# macOS
open ~/chromoplas-results/07_reports/report.html
```

The [demo gallery](demo-gallery.md) illustrates the output layout with **synthetic data**.

## 6. Output folders and files

| Folder | What you will find |
| --- | --- |
| `00_metadata/` | Input manifest and resolved configuration |
| `01_genomes/` | Working assembly FASTA |
| `02_quality/` | QC metrics and pass/fail decisions |
| `03_annotation/` | Optional Prokka output, **only when enabled** |
| `04_abricate/` | ARG, VF, and replicon screening |
| `05_plasmids/` | MOB-suite contig/plasmid predictions |
| `06_localization/<sample>/` | Contig/gene localization TSVs and `architecture.svg` |
| `07_reports/` | `report.html` and `master_summary.tsv` |

The chromosome/plasmid/unresolved calls are computational predictions. Unresolved assignments remain visible.

## 7. Commands you will use most

```bash
chromoplas --help
chromoplas doctor
chromoplas ~/Downloads/isolate.fna -o ~/preview --dry-run
chromoplas ~/Downloads/isolate.fna -o ~/chromoplas-results -t 4
conda deactivate
```

A first dry-run can show only early jobs because Snakemake expands downstream jobs after the QC checkpoint.

## 8. Common errors

| Error | Resolution |
| --- | --- |
| `hash: hashing disabled` | Run `set -h`; follow [Omarchy fix](install-omarchy.md) |
| Mamba shell not initialized | Initialize Conda as above; use `conda activate chromoplas` |
| `chromoplas: command not found` | Install the ChromoPlas package inside the activated environment |
| Missing ABRicate database | Run `abricate --list`; see [database update guide](updating.md) |
| QC `FAIL` | Inspect `02_quality/quality_summary.tsv` |

More: [Installation](../INSTALL.md) · [Commands](../command_help.md) · [Troubleshooting](troubleshooting.md).
