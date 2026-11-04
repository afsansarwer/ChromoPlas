# ChromoPlas release readiness checklist

## Before a public beta announcement

- [x] Source available with MIT license and citation guidance.
- [x] Beginner installation instructions for Linux and WSL2; macOS dependency compatibility explicitly qualified.
- [x] Synthetic examples clearly labeled, separate from real analysis output.
- [x] Actual workflow generates a gene localization matrix per sample.
- [x] Missing MGE evidence reported separately from observed zero.
- [x] Run-level provenance collected locally.
- [x] Python tests and a fully orchestrated **synthetic-tool** workflow check added.
- [ ] Complete at least one fully documented run using real ABRicate and MOB-suite with initialized databases.
- [ ] Cross-check predicted plasmid/chromosome location using independently characterized public assemblies.
- [ ] Demonstrate reproducible batch runs, no-hit assemblies and genuinely ambiguous contigs with real tools.
- [ ] Verify clean Debian/Ubuntu installation; note exact tool and database versions and installation issues.
- [ ] Confirm CI is green for the final release commit and inspect the rendered HTML and SVG.
- [ ] Create immutable version tag and GitHub beta release notes; archive with Zenodo after verification.

## Scientific communication rules

- Describe ChromoPlas as a **research prototype / public beta** until all reference validation gates pass.
- Do not claim clinical diagnosis, confirmed plasmid origin, complete MGE detection, or validated cross-platform operation.
- The integration test uses tool stubs; it checks workflow plumbing rather than biological accuracy.
- No citation DOI or paper should be claimed until one exists.
