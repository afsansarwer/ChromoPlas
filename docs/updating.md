# Update ChromoPlas, analysis tools, and reference databases

This guide applies to Linux, macOS, and Ubuntu/WSL2 installations using the **chromoplas** Miniforge environment. On Omarchy, fix Bash activation first using the [Omarchy guide](install-omarchy.md).

## Before updating

Updates to ABRicate databases or MOB-suite can alter detected hits and contig predictions. Archive your project's settings, database versions, and results before updating mid-study. Updates can require significant disk space and downloads.

For a separate Conda environment copy (does not include every external database):

~~~bash
source "$HOME/miniforge3/etc/profile.d/conda.sh"
conda create --name chromoplas-backup --clone chromoplas
~~~

## Update all managed tools and default databases

Run **in Bash or Zsh**, from the repository root:

~~~bash
# On Omarchy/Bash only: enable Bash hashing for Conda activation.
set -h
source "$HOME/miniforge3/etc/profile.d/conda.sh"
cd /path/to/your/genomeflow-clone
bash scripts/update-all.sh
~~~

The script asks you to type **UPDATE** before changes. It:

1. Saves Conda package manifests and the current Git commit.
2. Pulls the repository's latest code (fast-forward only).
3. Updates packages in the **chromoplas** Conda environment, retaining compatible Python 3.11 / Snakemake 8–9 versions, then reinstalls the ChromoPlas Python package.
4. Refreshes the **ResFinder, VFDB and PlasmidFinder** ABRicate databases.
5. Runs MOB-suite database initialization, then checks the CLI and Python unit tests.
6. Saves post-update environment and ABRicate database snapshots under **~/.local/share/chromoplas/update-snapshots/**.

The updater is **not a transactional rollback**. Existing biological database directories are not automatically backed up. If its external database commands fail, follow the upstream [ABRicate](https://github.com/tseemann/abricate) or [MOB-suite](https://github.com/phac-nml/mob-suite) setup documentation and inspect the error before retrying.

For unattended use, supply **--yes** only after reviewing the script. An optional **--bakta-db PATH** mode exists for an independently installed Bakta database; **Bakta is not part of ChromoPlas's default analysis workflow**.

## Verify the updated installation

~~~bash
conda activate chromoplas
chromoplas --help
chromoplas doctor
abricate --list
python -m pytest -q
~~~

Run a known assembled bacterial genome in a **new output directory** to verify full analysis after updating databases.

## Windows / WSL2

From PowerShell, enter Ubuntu:

~~~powershell
wsl -d Ubuntu
~~~

Then run the Bash updater steps **inside Ubuntu**, where the scientific tools are installed.

[Installation](../INSTALL.md) · [Troubleshooting](troubleshooting.md) · [Citations](../CITATION.md)
