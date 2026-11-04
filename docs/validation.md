# ChromoPlas: validation and scientific limitations

**Project stage: v0.3 research prototype.** The predecessor GenomeFlow v0.1 completed a 12-step run on one Linux bacterial assembly; the redesigned ChromoPlas workflow is not yet tested end to end. The new v0.3 CLI and the cross-platform installation guides have **not** been fully validated end to end on Debian, macOS or Windows/WSL2.

## What ChromoPlas does not do

- ChromoPlas accepts **assembled nucleotide FASTA**, not FASTQ; it does not trim or assemble raw reads.
- Assembly size, contig count, N50 and GC% are **not estimates of completeness or contamination**.
- Default quality thresholds are broad, **not species-specific**; customize for your data.
- Optional Prokka annotations are computational predictions; Bakta is not integrated in this version.
- ABRicate hits are reference database matches whose results depend on identity/coverage thresholds, assembly completeness and database version. Detection does not prove expression or phenotypic resistance; nondetection does not prove absence.
- MOB-suite plasmid assignment and reconstruction are **computational predictions**, not evidence of complete, experimentally verified or circular plasmids.
- No clinical diagnostic or antimicrobial prescribing claims are supported.

## Testing needed before a stable release

1. A clean install on Debian/Ubuntu, Intel macOS, Apple Silicon macOS and WSL2; document actual package-solving problems.
2. Single-genome and batch runs on published, well-characterized bacterial assemblies.
3. Known positive/negative ABRicate results and database-version checks.
4. Known plasmid-bearing and plasmid-negative assemblies, including missing/empty plasmid outputs.
5. Error handling for corrupt FASTA, missing tools/databases, duplicate sample identifiers, interruption/resume and bad output paths.
6. Performance/reproducibility checks with fixed reference versions and tool environments.
7. Review TSV and HTML reports for QC-failed assemblies and cross-sample aggregation before publication.

## Reproducibility checklist

Keep ChromoPlas repository commit/tag, input assembly accession and checksums, OS/architecture, full Conda environment export, Snakemake and external tool versions, ABRicate database names and version/date, MOB-suite database version, QC thresholds, full config, intermediate outputs and logs.

The minimal GitHub Actions Python tests are **not full pipeline integration tests**. Validate interpretations independently before using results in a manuscript.

## Reporting safeguards added for the public beta

- Missing or incompatible MOB-suite MGE coordinate reports are recorded as `NA`, not a biological zero; a corresponding `mge_evidence_status` column explains the reason.
- A gene detected on unresolved contigs alongside chromosome/plasmid hits gets a combined localization category, not an exclusive claim.
- `00_metadata/provenance.json` records input SHA-256 hashes, run settings, source commit when available, tool version checks and the ABRicate database listing.
- `gene_localization_matrix.svg` is generated from each genome's own feature summary; images in the demo gallery are explicitly synthetic.

**Still required for a validated release:** publicly documented complete analyses of real, independently characterized bacterial genomes; comparison to expected locations; clean installation on target systems. Automated tests alone are not a substitute.
