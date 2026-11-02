# GenomeFlow

A command-line workflow for bacterial **assembled FASTA** analysis: assembly QC → HQ selection → Prokka/Bakta annotation → ABRicate genome screening → MOB-suite plasmid reconstruction → plasmid ABRicate screening → TSV/HTML reports.

**Status: v0.2 research prototype.** The workflow has been run end-to-end on a user's bacterial assembly, but it is not yet validated across species, platforms, or large cohorts. No claim of error-free operation is made.

## Quick start

See [INSTALL.md](INSTALL.md) for full environment and database setup.

```bash
genomeflow isolate.fna -o results/ -t 4
genomeflow genomes/ -o batch_results/ -t 8
genomeflow --help
```

For advanced settings, see `examples/config.yaml`. See [command_help.md](command_help.md) for command reference.

## Results

The output includes `02_quality/quality_summary.tsv`, genome annotation under `03_annotation/`, ABRicate hits under `04_abricate/`, MOB-suite results under `05_plasmids/`, plasmid screening under `06_plasmid_abricate/`, and a `07_reports/report.html` plus master TSV summaries.

## Interpretation

- HQ selection is based on FASTA-derived metrics only, not CheckM2 completeness/contamination.
- Reconstructed plasmid sequences are predictions.
- A missing gene hit is not proof of biological absence; verify database versions and screening thresholds.
- Use separate output directories for distinct projects and keep config/logs for reproducibility.

## Development

```bash
python -m pytest -q
python -m compileall -q src
```

MIT licensed. Contributions and bug reports welcome.
