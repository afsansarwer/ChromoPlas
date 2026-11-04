# ChromoPlas troubleshooting

Start with [Installation and verification](../INSTALL.md). Most failures fall into one of four categories: shell activation, missing Python package, missing analysis tool, or missing reference database.

| Symptom | First check | Resolution |
| --- | --- | --- |
| **bash: hash: hashing disabled** | Bash command hashing: **set -o** | [Permanent Omarchy fix](install-omarchy.md) |
| **mamba shell not initialized** | Confirm whether you use Bash or Zsh | For Bash: **source ~/miniforge3/etc/profile.d/conda.sh** then **conda activate chromoplas** |
| **chromoplas: command not found** | **echo "$CONDA_DEFAULT_ENV"** | Activate chromoplas, then install the package from the repository root |
| **snakemake / abricate / mob_recon missing** | **command -v TOOL** | Run `bash INSTALL.sh` inside the clone, or use Conda to install missing packages into `chromoplas` |
| **No FASTA assemblies found** | Confirm input path/extension | Provide assembled .fna/.fa/.fasta (or .gz), not FASTQ |
| **Database error** | **abricate --list** | Install/refresh ABRicate databases and check MOB-suite reference data |
| **QC FAIL / only 00_metadata, 02_quality, 07_reports** | **02_quality/quality_summary.tsv** | All samples may have been filtered before gene screening; inspect the `status` and `reasons` columns, then choose scientifically justified QC thresholds |

## Omarchy / Arch: persistent Conda activation fix

In Bash, try the current-session fix:

~~~bash
set -h
source "$HOME/miniforge3/etc/profile.d/conda.sh"
conda activate chromoplas
~~~

For all new terminals, place **set -h** in your personal **~/.bashrc**, **after Omarchy's initialization and before Conda initialization**. Follow the [full Omarchy guide](install-omarchy.md) for safe backup, ordering, and checks. Do not use the Zsh hook in a Bash session.

## Environment and command verification

~~~bash
echo "$CONDA_DEFAULT_ENV"
command -v python chromoplas snakemake abricate mob_recon
chromoplas --help
abricate --list
chromoplas doctor
# From your repository root: bash scripts/check-install.sh
~~~

If the environment is active but chromoplas is missing, run from your **local repository root**:

~~~bash
python -m pip install --no-deps -e .
~~~

Without shell activation, you can check the installed package with:

~~~bash
"$HOME/miniforge3/bin/conda" run -n chromoplas chromoplas --help
~~~

## Reference databases

The default screening requires **resfinder, vfdb and plasmidfinder** in ABRicate, along with MOB-suite reference data. Their initial setup or refresh may download large files. See [Update tools and databases](updating.md) and the upstream [ABRicate](https://github.com/tseemann/abricate) / [MOB-suite](https://github.com/phac-nml/mob-suite) instructions.

A successful chromoplas doctor check is an environment check, not a guarantee that every reference dataset is initialized. Try one known assembled bacterial genome to verify actual execution.

## Rerun and report issues

If Snakemake stops, inspect the console and **results/.snakemake/log/**, fix the cause, and rerun with the **same output and input**. A first dry run can display only the QC-checkpoint jobs; dependent jobs expand after that checkpoint completes.

For support, [open an issue](https://github.com/afsansarwer/ChromoPlas/issues) including OS, CPU architecture, the command you ran, the relevant error, chromoplas version, and the external tool/database versions. Do not upload sensitive research data.

## No SVG maps or plasmid/ABRicate folders after the run

If the output contains only `00_metadata/`, `02_quality/`, and `07_reports/`, first check:

```bash
cat /path/to/results/02_quality/quality_summary.tsv
cat /path/to/results/07_reports/master_summary.tsv
cat /path/to/results/00_metadata/hq_samples.txt
```

ChromoPlas screens only genomes that pass its **basic assembly QC**. By default, assemblies with more than **500 contigs** or more than **15,000,000 bp** fail the broad gates; these thresholds are not species-specific. If every genome fails QC, no gene screening, plasmid prediction or SVG is created. This is **not** evidence of absent genes. From the updated CLI, this case prints a clear explanation and exits with status **2**, although the QC-only HTML report is retained. Excluded specimens have `NA` counts rather than biological zeroes.

Adjust thresholds **only after inspecting the assembly's properties**. For an exploratory run where higher fragmentation is expected, create a YAML containing just the changed threshold, e.g.:

```yaml
quality:
  max_contigs: 1000
```

and rerun using a **new output directory**:

```bash
chromoplas /path/to/assembly.fna -o ~/chromoplas-relaxed-qc -t 4 --config /path/to/custom.yaml
```

Choose the threshold for the biological context; relaxing QC is not itself an improvement to assembly quality. Output tables and figures describe computational predictions only.
