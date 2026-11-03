# ChromoPlas

**From assembled bacterial genomes to contig-level chromosome/plasmid localization of antimicrobial resistance genes, virulence factors, and mobile genetic elements.**

ChromoPlas is an open-source, **lightweight bacterial genome analysis pipeline** built with Python and Snakemake. It independently screens each input genome, predicts which assembled contigs are chromosome-associated or plasmid-associated, joins gene calls to **original contig IDs and nucleotide coordinates**, and creates informative tables and an assembly-scale SVG figure.

> **Release status: v0.3 development candidate.** ChromoPlas is not yet validated on clean installations or broad biological test sets. It is not a clinical diagnostic. The previous GenomeFlow v0.2 is replaced by a new Python package and CLI.

## Main workflow

**Assembled FASTA** → **fast QC** → **ABRicate gene screening + MOB-suite contig classification** → **coordinate-level localization** → **SVG architecture map + per-isolate HTML/TSV report**

What it does:

- Calculates genome length, contig count, N50 and GC% and records QC pass/fail reasons.
- Screens original assembled contigs with ABRicate using **ResFinder (ARG)**, **VFDB (virulence factor)** and **PlasmidFinder (replicon markers)** by default.
- Runs **MOB-suite** to predict chromosome/plasmid assignments and plasmid group IDs.
- Maps each feature to its exact original contig and start/end positions; **unassigned/ambiguous contigs remain unresolved**.
- Detects repetitive/mobile-element matches from MOB-suite's **MGE report when available (version 3.1+)**. These are *putative MGE matches*, not a comprehensive catalog.
- Groups a gene as **chromosome-only**, **plasmid-only**, **both**, or **unresolved** from observed hit locations; unresolved hits are retained separately in the summary.
- Produces **all-contig** chromosome/plasmid/unresolved assembly diagrams (SVG), feature tables and an HTML report.
- Accepts one genome or several independently analyzed genomes. **No pangenome, SNP phylogeny, ANI or across-isolate comparative inference.**

**Scientific caution:** MOB-suite assignments are predictions; a contig labeled chromosome is not independently proven chromosomal. Reconstructed plasmid groups are not guaranteed complete/circular. The basic assembly QC does not measure completeness or contamination. CheckM2 is a planned *optional* feature, not yet implemented.

## Quick start

Installation requires a Linux-compatible environment with **Snakemake, ABRicate, and MOB-suite**, their reference databases, and Python. See [installation instructions](INSTALL.md).

~~~bash
chromoplas genome.fna -o results/ -t 4
chromoplas assembled_genomes/ -o batch_results/ -t 8
chromoplas genome.fna -o results/ --dry-run
chromoplas doctor
chromoplas --help
~~~

**Input:** assembled \`.fna\`, \`.fasta\`, \`.fa\`, including \`.gz\` variants. **Not input:** FASTQ reads. Use a **fresh output directory for each independent cohort** to avoid mixing previous Snakemake results.

## Outputs

~~~text
results/
├── 00_metadata/                   Manifest, resolved configuration
├── 01_genomes/                    Working genome FASTA
├── 02_quality/                    FASTA metrics and QC pass/fail list
├── 04_abricate/                   Per-database, per-isolate hits on original contigs
├── 05_plasmids/                   MOB-suite predictions, contig report and MGE report
├── 07_localization/<sample>/
│   ├── contig_summary.tsv         Original contig + predicted genomic compartment
│   ├── feature_localization.tsv   Each ARG/VF/MGE/replicon hit with coordinates
│   ├── gene_localization_summary.tsv
│   └── architecture.svg           All-contig genome-architecture figure
└── 07_reports/
    ├── report.html                Self-contained report index with linked SVG files
    └── master_summary.tsv
~~~

Optional Prokka annotation (default **disabled** to save computation) writes to \`03_annotation/\` when \`annotation.enabled: true\` in custom YAML. There is no separate plasmid ABRicate pass: gene localization uses matches to **original contig sequences**, avoiding duplicated screening and loss of original coordinates.

## Figure design

The architecture figure displays the **assembled genome as contig-level tracks**, grouped into chromosome-associated, plasmid-associated (sorted by MOB-suite plasmid cluster), and unresolved contigs. Bar lengths are scaled to each contig's length, and feature markers are placed at their original reference coordinates. Every contig is included; large fragmented assemblies produce tall SVGs.

ARG, VF and MGE are colored separately. PlasmidFinder hits are included as **Replicon** entries in tables. MOB-suite primary plasmid clusters are **predicted groupings**, not experimentally verified plasmids.

## Documentation

- [Install (Debian / Ubuntu, macOS, Windows via WSL2)](INSTALL.md)
- [Command reference](command_help.md)
- [QC and limitations](docs/validation.md)
- [Developer-oriented architecture/data definitions](docs/architecture.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Updating the Conda tools and databases](docs/updating.md)
- [How to cite the software and underlying tools](CITATION.md)

## Development and validation

~~~bash
python -m pip install -e '.[test]'
python -m pytest -q
python -m compileall -q src
~~~

These unit tests validate interpretation on synthetic input. A **real end-to-end ChromoPlas run** remains required before a stable tagged release.

License: [MIT](LICENSE). Current repository URL: https://github.com/afsansarwer/genomeflow (GitHub project rename to \`chromoplas\` is a separate owner action).
