# GenomeFlow

**Bacterial genome analysis from assembled FASTA to annotated genes, antimicrobial-resistance screening, predicted plasmids, and a readable report — with one command.**

GenomeFlow is an open-source Python CLI and Snakemake workflow for **assembled bacterial genomes**. It integrates familiar bioinformatics software into a repeatable process designed for microbiology, antimicrobial resistance (AMR), plasmid genomics and One Health research.

~~~bash
genomeflow genome.fna -o results/ -t 4
genomeflow genomes/ -o batch_results/ -t 8
~~~

> **Status: GenomeFlow v0.2 — research prototype.** A previous Linux version completed an end-to-end run on one bacterial isolate. **Debian/Ubuntu, macOS and Windows/WSL2 installation paths have not yet been validated end to end.** Do not treat results as clinical diagnostics; independently verify biological conclusions.

## What GenomeFlow actually does

| Analysis stage | Output | Engine |
| --- | --- | --- |
| Assembly QC and HQ selection | Assembly length, contigs, N50, GC% and configurable pass/fail | Python |
| Genome annotation | Predicted genes and annotated sequences | Prokka (default); Bakta optional |
| Whole-genome screening | AMR, virulence factor and plasmid replicon matches | ABRicate (ResFinder, VFDB, PlasmidFinder by default) |
| Plasmid reconstruction | Predicted plasmid-associated sequences | MOB-suite |
| Predicted plasmid screening | Gene/replicon matches in plasmid predictions | ABRicate |
| Consolidated reporting | Quality TSV, hits TSV, summary TSV and HTML report | Snakemake/Python |

**Input:** assembled nucleotide genome \`.fna\`, \`.fasta\`, \`.fa\`, optional \`.gz\`, either a single file or folder. **Not supported:** FASTQ read trimming, genome assembly, contamination/completeness estimates, phylogeny, or experimentally proving plasmid location.

## Installation

Choose an operating-system guide:

| Platform | Documentation | Support |
| --- | --- | --- |
| Debian / Ubuntu | [Linux instructions](docs/install-debian.md) | Recommended starting environment; distribution-specific validation pending |
| macOS Intel and Apple Silicon | [macOS instructions](docs/install-macos.md) | Experimental: native dependency availability varies |
| Windows PowerShell | [Windows + WSL2 instructions](docs/install-windows-powershell.md) | Experimental PowerShell wrapper launching Ubuntu/WSL2, **not native Windows binaries** |
| Other Linux | [Installation overview](INSTALL.md) | Linux tools required |

GenomeFlow needs an environment with Snakemake, Prokka, ABRicate, MOB-suite and their reference databases. The Python package alone **does not include these external tools or databases**.

## Quick start (after installation)

~~~bash
genomeflow isolate.fna -o results -t 4
genomeflow assemblies/ -o batch_results -t 8
genomeflow isolate.fna -o results -t 4 --dry-run
genomeflow --help
~~~

The first Snakemake dry run may show only a small number of jobs because its QC-selection checkpoint expands the downstream dependency graph after execution.

## Results layout

~~~text
results/
├── 00_metadata/            # Manifest and resolved configuration
├── 01_genomes/             # Working genome FASTA files
├── 02_quality/             # Quality summary and passing samples
├── 03_annotation/          # Annotation output
├── 04_abricate/            # Whole-genome database screening
├── 05_plasmids/            # MOB-suite plasmid predictions
├── 06_plasmid_abricate/    # Plasmid-derived sequence screening
└── 07_reports/
    ├── report.html
    ├── master_summary.tsv
    └── all_abricate_hits.tsv
~~~

**Scientific cautions:** QC based on assembly statistics is not CheckM2-like completeness/contamination analysis. ABRicate matches depend on thresholds and reference database versions. MOB-suite plasmid predictions should not be interpreted as experimentally confirmed plasmids.

## Documentation and community

- [Installation overview](INSTALL.md)
- [Command reference](command_help.md)
- [Debian/Ubuntu](docs/install-debian.md) · [macOS](docs/install-macos.md) · [Windows PowerShell + WSL2](docs/install-windows-powershell.md)
- [Troubleshooting](docs/troubleshooting.md)
- [Validation, limitations and reproducibility](docs/validation.md)
- [Report problems or suggest features](https://github.com/afsansarwer/genomeflow/issues)

The test suite can be run with \`python -m pytest -q\`; these are **unit tests**, not full cross-platform biological validation. **License:** MIT ([LICENSE](LICENSE)).
