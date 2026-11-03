# ChromoPlas

**Bacterial genome screening and chromosome–plasmid gene localization, from assembled FASTA to interpretable figures.**

ChromoPlas is a lightweight Python/Snakemake pipeline that screens assembled bacterial genomes for antimicrobial resistance genes (ARGs), virulence factors (VFs), plasmid replicon markers and available mobile genetic element (MGE) matches. It maps features to their **original contigs and coordinates**, predicts chromosome/plasmid association using MOB-suite, and generates a whole-assembly SVG plus HTML and TSV reports.

![Python tests](https://github.com/afsansarwer/genomeflow/actions/workflows/tests.yml/badge.svg)

## Quick start

~~~bash
chromoplas genome.fna -o results/ -t 4
chromoplas genomes/ -o batch_results/ -t 8
chromoplas doctor
~~~

**Inputs:** assembled .fna / .fa / .fasta files (plain or .gz). Each isolate is analyzed independently; pangenome and across-isolate comparisons are not required.

## Workflow

| Stage | Software | Result |
| --- | --- | --- |
| Assembly QC | ChromoPlas | Genome length, contigs, N50, GC%, pass/fail |
| Gene screening | ABRicate (ResFinder, VFDB, PlasmidFinder) | ARG, VF and replicon matches |
| Contig classification | MOB-suite | Chromosome, plasmid group or unresolved |
| MGE localization | Available MOB-suite MGE report | Coordinate-linked MGE matches |
| Genome map | ChromoPlas | All-contig SVG and per-isolate HTML/TSV |

**Figure:** every assembly contig, grouped by predicted genomic compartment, with color-coded gene hits at contig coordinates. Gene summaries distinguish detections on chromosomes, plasmids, both, or unresolved contigs. Optional Prokka annotation is available via YAML.

## Output highlights

~~~text
results/
├── 02_quality/quality_summary.tsv
├── 04_abricate/                         # Gene screens
├── 05_plasmids/                         # MOB-suite results
├── 07_localization/<sample>/
│   ├── contig_summary.tsv
│   ├── feature_localization.tsv
│   ├── gene_localization_summary.tsv
│   └── architecture.svg
└── 07_reports/
    ├── report.html
    └── master_summary.tsv
~~~

Open the HTML report in your browser to explore the contig-level figures and gene summaries.

## Install and use

**[Installation overview](INSTALL.md)** · [Debian/Ubuntu](docs/install-debian.md) · [Omarchy/Arch (Conda fix)](docs/install-omarchy.md) · [macOS](docs/install-macos.md) · [Windows/WSL2 PowerShell](docs/install-windows-powershell.md)

**[Command reference](command_help.md)** · [Update tools/databases](docs/updating.md) · [Troubleshooting](docs/troubleshooting.md) · [Citations](CITATION.md) · [Scientific interpretation](docs/validation.md)

**Version:** 0.3.0 · **Author:** Afsan Sarwer · **License:** [MIT](LICENSE)

The workflow reports computational chromosome/plasmid predictions and preserves ambiguous contigs as **unresolved**. See [validation notes](docs/validation.md) for scientific interpretation and current testing scope.
