# ChromoPlas release readiness checklist

## Before a public beta announcement

- [x] Source available with MIT license and citation guidance.
- [x] Beginner installation instructions for Linux and WSL2; macOS dependency compatibility explicitly qualified.
- [x] Synthetic examples clearly labeled, separate from real analysis output.
- [x] Actual workflow generates a gene localization matrix per sample.
- [x] Missing MGE evidence reported separately from observed zero.
- [x] Run-level provenance collected locally.
- [x] Python tests and a fully orchestrated **synthetic-tool** workflow check added.
- [x] Complete one current-version run with real ABRicate and MOB-suite on Linux (5 November 2026; completed 9/9 workflow steps; report rendered).
- [ ] Publish a reproducible, accession-based worked example with real-tool output, exact database versions and expected-versus-observed evidence.
- [ ] Cross-check predicted plasmid/chromosome location using independently characterized public assemblies.
- [ ] Demonstrate reproducible batch runs, no-hit assemblies and genuinely ambiguous contigs with real tools.
- [ ] Verify clean Debian/Ubuntu installation; note exact tool and database versions and installation issues.
- [x] CI passed on Python 3.11 and 3.12 for release-hardening commit `77729a9`.
- [ ] Confirm CI is green for the final release commit and publish a redacted, reproducible rendered HTML/SVG example.
- [ ] Create immutable version tag and GitHub beta release notes; archive with Zenodo after verification.

## Evidence recorded

A real single-genome workflow on Omarchy Linux was completed on 2026-11-05, using the assembled input and installed ABRicate/MOB-suite databases; the screenshot showed 9/9 completed jobs, QC PASS and a rendered HTML report. This is an execution smoke test, not independently verified plasmid or gene-placement accuracy. Input identifiers, local usernames and unpublished data must not be copied into public materials.

## Scientific communication rules

- Describe ChromoPlas as a **research prototype / public beta** until all reference validation gates pass.
- Do not claim clinical diagnosis, confirmed plasmid origin, complete MGE detection, or validated cross-platform operation.
- The integration test uses tool stubs; it checks workflow plumbing rather than biological accuracy.
- No citation DOI or paper should be claimed until one exists.
