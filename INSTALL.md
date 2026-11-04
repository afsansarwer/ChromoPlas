# Install ChromoPlas

## Recommended: one installer command (Ubuntu/Debian/WSL2)

From inside a cloned ChromoPlas repository:


```bash
bash INSTALL.sh
```

Use the **Linux terminal**, not PowerShell. The installer supports Debian/Ubuntu x86_64 (including WSL2), and it works when the interactive shell is **Bash or Zsh**. It detects existing Miniconda, Miniforge, or Anaconda installations; otherwise it downloads the official Miniforge installer and verifies its SHA256 checksum. No Mamba command is required.

What it does:

1. Finds or installs Conda; never installs the pipeline into `(base)`.
2. Creates or repairs the dedicated `chromoplas` Conda environment (Python 3.11, Snakemake 8/9, ABRicate, MOB-suite and Python dependencies).
3. Installs ChromoPlas inside that environment, independently of the active shell.
4. Checks the required ResFinder/VFDB/PlasmidFinder ABRicate databases, setting them up if absent, and initializes MOB-suite reference data if needed.
5. Runs `chromoplas doctor` and the installation checker. **Any failure stops the script**; no false success message.

**The first setup requires internet access, available disk space and may download large reference datasets.** The installer does not edit your `~/.bashrc` or `~/.zshrc`. Do not invoke it with sudo.

After it completes:


```bash
conda activate chromoplas
chromoplas --help
chromoplas doctor
```

If your shell has not initialized Conda, use the `source .../etc/profile.d/conda.sh` command printed at the end of installation, then activate. **Each new shell requires activation**.

## If you already have Conda and prefer manual installation

These commands work in **Bash and Zsh**, from the cloned repository directory:


```bash
conda create -y -n chromoplas --override-channels -c conda-forge -c bioconda \
  'python=3.11' 'snakemake>=8,<10' abricate mob_suite typer pyyaml pip pytest
conda activate chromoplas
python -m pip install --no-deps -e .
abricate --list
chromoplas doctor
```

For missing ABRicate databases, run `abricate --setupdb`; for MOB-suite data, run `mob_init`. Both commands operate only after activating `chromoplas`. If that environment already exists, skip `conda create` or run `bash INSTALL.sh` to install or repair dependencies safely.

**Your observed beginner error:**

- `zsh: command not found: mamba`: Mamba is not required; this project now uses Conda.
- `EnvironmentNameNotFound: chromoplas`: environment creation failed; do not continue with `pip install` while `(base)` is active.
- `chromoplas --help` works in `(base)` but `abricate`/`mob_recon` are missing: the Python CLI was installed into the wrong environment. Run the guided installer and then `conda activate chromoplas`; you do **not** need to uninstall the old base copy to run the correct environment.

## First run


```bash
chromoplas examples/genomes/test_isolate.fna -o ~/chromoplas-preview --dry-run
chromoplas ~/genomes/genome.fna -o ~/chromoplas-results -t 4
chromoplas ~/genomes/ -o ~/chromoplas-batch -t 8
```

Open `~/chromoplas-results/07_reports/report.html` when the real analysis finishes. Input: assembled bacterial FASTA, not FASTQ.

## Other platforms and advanced help

| Platform | Guide |
| --- | --- |
| Debian/Ubuntu Linux | [Detailed setup](docs/install-debian.md) |
| Windows with WSL2 | [WSL2 instructions](docs/install-windows-powershell.md) |
| Omarchy / Arch | [Conda hashing fix](docs/install-omarchy.md) |
| macOS Intel/Apple Silicon | [Manual setup; compatibility varies](docs/install-macos.md) |

[Beginner's guide](docs/beginners-guide.md) · [Troubleshooting](docs/troubleshooting.md) · [Command reference](command_help.md) · [Update tools/database versions](docs/updating.md) · [Validation limits](docs/validation.md)

**Science note:** successful installation and execution do not establish independently benchmarked biological accuracy; ChromoPlas v0.3.0 remains public beta.
