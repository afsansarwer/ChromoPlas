# Conda and Mamba: a short beginner guide

**Conda** creates and activates software environments; **Mamba** is a fast package resolver and installer for compatible Conda packages. ChromoPlas itself is a Python package, installed with `pip` after creating its environment.

## What each command does

| Command | Meaning |
| --- | --- |
| `source ~/miniforge3/etc/profile.d/conda.sh` | Prepare the current shell for Conda activation |
| `conda activate chromoplas` | Enter the ChromoPlas environment |
| `mamba install -n chromoplas -c conda-forge -c bioconda PACKAGE` | Install a package into the environment |
| `python -m pip install --no-deps -e .` | Install the ChromoPlas CLI from its cloned repository |
| `conda deactivate` | Leave the active environment |
| `conda env list` | Show available environments |

## Omarchy Bash fix

Omarchy may disable Bash command hashing. If activation prints `bash: hash: hashing disabled`, run `set -h` **before** initializing Conda. Follow the [permanent setup instructions](install-omarchy.md) for your own `~/.bashrc`.

## Check that tools exist

```bash
conda activate chromoplas
chromoplas --help
chromoplas doctor
abricate --list
```

If Conda cannot activate, you can run a command without activation:

```bash
"$HOME/miniforge3/bin/conda" run -n chromoplas chromoplas --help
```

See [installation](../INSTALL.md) and the [beginner guide](beginners-guide.md).