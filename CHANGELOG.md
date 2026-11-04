# Changelog

## v0.3.0 — public beta candidate (November 2026)

- First documented complete current-version analysis of a real bacterial assembly on Omarchy Linux (2026-11-05); 9/9 workflow steps completed and the HTML report rendered. This is **execution evidence**, not independent accuracy benchmarking.
- Release notes and publication communication now distinguish completed real execution from pending reference validation.

### Public-beta hardening

- Corrected GitHub repository URLs after the ChromoPlas rename.
- Made `chromoplas doctor` fail when required ABRicate databases are missing.
- Distinguished missing/unusable MGE coordinate evidence (`NA`) from genuine zero observed coordinate-resolved hits.
- Preserved unresolved contig evidence when the same gene also occurs on a predicted chromosome or plasmid.
- Added a per-sample `gene_localization_matrix.svg` generated from actual feature tables, distinct from synthetic promotional figures.
- Added `00_metadata/provenance.json` with input checksums, workflow revision when available, tool version output and database listing.
- Added focused tests and a synthetic full-workflow integration test using simulated external tools.

**Validation status:** research prototype. A synthetic orchestration test is not evidence of real ABRicate/MOB-suite scientific accuracy. Real bacterial reference assemblies and clean multi-platform installations remain to be validated before a stable release.
