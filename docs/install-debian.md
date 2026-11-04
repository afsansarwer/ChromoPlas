# Debian / Ubuntu / WSL2 installation

**For most users, the whole installation is three commands** in the Debian/Ubuntu terminal (Bash or Zsh):


```bash
git clone https://github.com/afsansarwer/ChromoPlas.git
cd ChromoPlas
bash INSTALL.sh
```

The guided installer supports **x86_64** Linux and WSL2, detects your existing Conda, installs Miniforge when missing, creates the separate `chromoplas` Conda environment, installs all required tools and databases, then checks the installation. It does not use Mamba, and it stops on failure.

**Already cloned?** Do not clone again: go into your `ChromoPlas` directory and execute `bash INSTALL.sh`.

**Using Zsh?** The commands work the same way. Do not install into your Conda `(base)` environment.

### After installation


```bash
conda activate chromoplas
chromoplas doctor
chromoplas --help
chromoplas examples/genomes/test_isolate.fna -o ~/chromoplas-preview --dry-run

# Replace this with your own assembled bacterial genome
chromoplas ~/genomes/genome.fna -o ~/chromoplas-results -t 4
```

Results: `~/chromoplas-results/07_reports/report.html`.

### WSL2 files

Prefer Linux home directory (`~/genomes/`, `~/chromoplas-results/`) for input and output. Windows-mounted `/mnt/c` and `/mnt/e` may be slower or cause filesystem/symlink issues. The repository clone itself can be on a Windows-mounted drive if necessary.

### Troubleshooting

- `chromoplas: command not found` after cloning: run `bash INSTALL.sh`. Cloning alone does not install anything.
- `mamba: command not found`: irrelevant; this installer uses Conda only.
- `EnvironmentNameNotFound`: Conda setup did not finish. Rerun the installer; do not install packages from `(base)`.
- `conda activate` is unavailable: follow the `source .../conda.sh` command printed by the installer.
- `chromoplas doctor` fails: inspect the shown missing tools/databases, or check `abricate --list`.
- MOB-suite's reference data can require a **large** first-time download.

See [main installation guide](../INSTALL.md), [beginner guide](beginners-guide.md), [troubleshooting](troubleshooting.md), and [scientific limitations](validation.md).
