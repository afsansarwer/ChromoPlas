# ChromoPlas

### Map resistance and virulence determinants to bacterial chromosomes and plasmids

**ChromoPlas** is a lightweight, open-source bacterial genomics pipeline that turns assembled genomes into **contig-resolved gene localization maps**. It identifies antimicrobial resistance genes (ARGs), virulence factors (VFs), plasmid replicon markers, and available mobile genetic element (MGE) matches, then combines these findings with predicted chromosome/plasmid assignments.

Give ChromoPlas a single assembled genome or a folder of genomes. Each isolate receives its own analysis, figures, and searchable results.

![Python tests](https://github.com/afsansarwer/genomeflow/actions/workflows/tests.yml/badge.svg)

## At a glance

| Step | Analysis | Output |
| --- | --- | --- |
| 1. Genome QC | Genome size, contig count, N50, GC content | Quality summary and selection |
| 2. Gene screening | ResFinder, VFDB, PlasmidFinder using ABRicate | Gene and replicon matches with coordinates |
| 3. Contig classification | MOB-suite plasmid reconstruction and contig assignments | Chromosome-associated, plasmid-associated, and unresolved contigs |
| 4. Localization | Integrate gene coordinates, contig assignments, and available MOB-suite MGE matches | Per-contig ARG/VF/MGE localization tables |
| 5. Visualization | Draw every assembled contig with gene markers | Genome architecture SVG and HTML report |

### What the figure shows

- The **whole assembly** represented by its original contigs, scaled by length.
- Contigs grouped into **chromosome-associated**, **plasmid-associated**, and **unresolved**.
- Plasmid-associated contigs organized by their predicted MOB-suite plasmid cluster.
- Color-coded ARG, VF, and MGE detections at their contig-relative positions.
- Gene-level summaries showing **chromosome only**, **plasmid only**, **both**, or **unresolved** detection.

No pangenome, phylogeny, or all-versus-all genome comparison is required. ChromoPlas is designed to keep each isolate's workflow focused.

## Quick start

Once installed:

~~~bash
# Analyze one assembled genome
chromoplas isolate.fna -o results/ -t 4

# Analyze a directory of assemblies independently
chromoplas genomes/ -o batch_results/ -t 8

# Check the installation
chromoplas doctor
~~~

Accepted input: assembled bacterial .fna, .fasta, or .fa files, including gzip-compressed versions.

### Installation guides

| Platform | Guide |
| --- | --- |
| Debian / Ubuntu | [Step-by-step Linux installation](docs/install-debian.md) |
| macOS | [Intel and Apple Silicon](docs/install-macos.md) |
| Windows | [PowerShell with Ubuntu/WSL2](docs/install-windows-powershell.md) |

For a shorter overview, see [INSTALL.md](INSTALL.md).

## Results

~~~text
results/
├── 02_quality/
│   └── quality_summary.tsv
├── 04_abricate/                   # Per-database screening results
├── 05_plasmids/                   # MOB-suite plasmid/contig assignments
├── 07_localization/
│   └── isolate/
│       ├── contig_summary.tsv
│       ├── feature_localization.tsv
│       ├── gene_localization_summary.tsv
│       └── architecture.svg
└── 07_reports/
    ├── report.html
    └── master_summary.tsv
~~~

Open results/07_reports/report.html in a browser to explore the results and contig map. The TSV files are suitable for downstream analysis, figure preparation, and manuscript methods.

## Workflow options

ChromoPlas uses **Snakemake** for reproducible job execution, **ABRicate** for gene screening, and **MOB-suite** for contig/plasmid assignment. The default workflow avoids unnecessary annotation to keep execution lightweight. Prokka can be enabled as an optional annotation step.

For advanced configuration, thresholds and commands, see the [command guide](command_help.md) and [workflow architecture](docs/architecture.md).

## Documentation

[Installation](INSTALL.md) · [Commands](command_help.md) · [Update tools and databases](docs/updating.md) · [Troubleshooting](docs/troubleshooting.md) · [Citations](CITATION.md) · [Scientific interpretation and validation](docs/validation.md)

## Project information

**Version:** 0.3.0 · Automated Python tests and workflow planning checks are available.

**Interpretation:** Chromosomal and plasmid assignments are computational predictions. Ambiguous contigs are reported as **unresolved** rather than being assigned by assumption.

**License:** [MIT](LICENSE) · **Author:** Afsan Sarwer · [Report an issue](https://github.com/afsansarwer/genomeflow/issues)
