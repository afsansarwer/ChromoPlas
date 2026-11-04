# Contributing to ChromoPlas

Thanks for testing or improving ChromoPlas.

## Reporting a bug

Open a [GitHub issue](https://github.com/afsansarwer/ChromoPlas/issues) with:

- ChromoPlas version/commit, OS, architecture and installation method.
- The command executed and relevant error output.
- The `00_metadata/provenance.json` tool/database information, after checking it for local file paths or other sensitive information.
- A **small synthetic or public-data reproduction** when possible. Do not submit restricted or unpublished genomic data without permission.

## Development

Use a dedicated Conda environment, install with `python -m pip install --no-deps -e .`, then run:

```bash
python -m pytest -q
python -m compileall -q src
chromoplas doctor
```

For scientific changes, add expected-versus-observed tests and explain how chromosome/plasmid/unresolved uncertainty is handled. Never introduce implicit classification of ambiguous contigs as chromosomes. Keep externally sourced tools and database licensing/citations clear.

Open a pull request with a short description, tests, and any changes to biological interpretation. Unit tests, synthetic workflow orchestration, and *real genome validation* must be described separately.
