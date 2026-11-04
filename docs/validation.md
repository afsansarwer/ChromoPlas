# ChromoPlas: validation and scientific limitations

**Project stage: v0.3 public beta / research prototype.** One end-to-end analysis with the current ChromoPlas CLI, real ABRicate and MOB-suite tools, and an assembled bacterial genome completed on Omarchy (Arch-based Linux) on **5 November 2026**. The Snakemake run completed **9/9 steps**, QC passed, and the HTML report rendered. This establishes successful execution of that particular configuration and input; it **does not independently establish** the accuracy of plasmid/chromosome predictions or transferability to every supported OS. The input assembly and its result tables have not been published as a reproducible benchmark. The cross-platform install guides have not been fully verified on all platforms.

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

GitHub Actions includes Python tests, workflow planning and full **synthetic tool-stub** orchestration tests. The local run on 5 November 2026 exercised real ABRicate and MOB-suite; neither class of test independently verifies biological classifications. Validate interpretations against well-characterized public reference assemblies before using results in scientific conclusions.

## Reporting safeguards added for the public beta

- Missing or incompatible MOB-suite MGE coordinate reports are recorded as `NA`, not a biological zero; a corresponding `mge_evidence_status` column explains the reason.
- A gene detected on unresolved contigs alongside chromosome/plasmid hits gets a combined localization category, not an exclusive claim.
- `00_metadata/provenance.json` records input SHA-256 hashes, run settings, source commit when available, tool version checks and the ABRicate database listing.
- `gene_localization_matrix.svg` is generated from each genome's own feature summary; images in the demo gallery are explicitly synthetic.

**Still required for a stable, independently validated release:** publish a reproducible worked analysis using a public genome accession and fixed reference versions; compare predicted gene/contig locations with independently characterized chromosome/plasmid truth; verify relevant edge cases and additional target OS installations. A completed real-genome run alone does not demonstrate benchmark accuracy.
