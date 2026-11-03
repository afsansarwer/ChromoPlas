# Updating ChromoPlas, analysis tools and reference databases

ChromoPlas has a **single Linux/macOS/WSL2 maintenance command** for its Conda-based installation. The updater refreshes the GitHub source, **all packages in the `chromoplas` Conda environment**, the **three default ABRicate databases**, and the **MOB-suite reference data**. Bakta is optional and requires an explicit database path.

**Important:** This is a research prototype updater. It has not yet been exercised on every operating system or package combination. Back up valuable research outputs, do not interrupt database setup, and **do not change versions halfway through a comparative study**.

## One-command update (Linux, Debian/Ubuntu, macOS or WSL2 Ubuntu)

First enter your existing clone and initialize Miniforge:

```bash
cd ~/chromoplas  # OR wherever you cloned ChromoPlas
source "$HOME/miniforge3/etc/profile.d/conda.sh"
conda activate base
bash scripts/update-all.sh
```

The script prompts you to type `UPDATE` before installing/updating packages and downloading databases. To run noninteractively:

```bash
bash scripts/update-all.sh --yes
```

**Optional Bakta reference database:** if Bakta is installed in the same environment and your analysis uses an existing Bakta DB, use:

```bash
bash scripts/update-all.sh --bakta-db /absolute/path/to/bakta/db
```

The script will not install Bakta automatically or guess where its optional database is stored. For an alternative installation environment/location, customize the script rather than assuming the defaults.

## What the script updates

| Component | Operation |
| --- | --- |
| ChromoPlas source | `git pull --ff-only`; refuses a dirty working tree |
| Python and all Conda packages in `chromoplas` | `mamba update --all`; temporary pins preserve Python 3.11 and Snakemake 8/9 |
| Required analysis programs | Rechecks/install constraints for Snakemake, ABRicate, MOB-suite and Python packages (Prokka is optional) |
| ChromoPlas Python package | Reinstalls in editable mode with `python -m pip install --no-deps -e .` |
| ResFinder, VFDB, PlasmidFinder | Downloads fresh available ABRicate database sources using `abricate-get_db --db NAME --force` and rebuilds indices |
| MOB-suite | Runs upstream `mob_init` to download/reinitialize its database; **large download**, may also refresh taxonomy data |
| Bakta (optional) | Runs upstream `bakta_db update --db PATH` **only when requested** |
| Post-update checks | ChromoPlas help, Python unit tests, version/environment and ABRicate DB snapshots |

ABRicate database refresh follows [ABRicate's upstream instructions](https://github.com/tseemann/abricate#updating-the-databases); MOB-suite initialization follows its [upstream README](https://github.com/phac-nml/mob-suite); Bakta updating follows its [upstream README](https://github.com/oschwengers/bakta). The word **latest** means the newest version/data available to each package source at update time—not a guarantee all sources are synchronized or free of errors.

## Snapshots and rollback

Before changing the Conda environment, the updater saves its explicit package list and YAML export; after updating it writes new snapshots and the ABRicate database list. They are saved under:

```text
~/.local/share/chromoplas/update-snapshots/YYYYMMDDTHHMMSSZ/
```

These files support **manual restoration** and reproducibility but are **not an automatic rollback mechanism**. Biological databases are **not copied** as part of the snapshot and can be large; archive their files or release data separately if you need bit-for-bit reproducibility.

For important studies, best practice is to **clone the original environment** or use a separate installation before a broad update:

```bash
conda create --name chromoplas-backup --clone chromoplas
```

The clone is a package/environment backup, **not** a full copy of all external databases, input files, or results. Repository code also changes during the update; retain the commit hash in your methods.

## Updating from Windows PowerShell

PowerShell executes the **Ubuntu/WSL2** installation; it does not update native Windows executables.

From Windows PowerShell, start Ubuntu:

```powershell
wsl -d Ubuntu
```

Then **inside Ubuntu**, run:

```bash
cd ~/chromoplas
source "$HOME/miniforge3/etc/profile.d/conda.sh"
conda activate base
bash scripts/update-all.sh
```

If the WSL distribution is named `Ubuntu-24.04`, use `wsl -d Ubuntu-24.04`. See [Windows PowerShell installation](install-windows-powershell.md).

## How to verify

```bash
conda activate chromoplas
chromoplas --help
snakemake --version
abricate --version
abricate --list
mob_recon --version
python -m pytest -q
```

For a biological test, rerun one **well-characterized real bacterial genome** in a **new output directory** and inspect `07_reports/report.html`. Empty datasets, broken databases or altered screening results require investigation before publication.

## Reproducibility warning

Database updates can change gene names, reference composition, hits, and predicted plasmid assignments. If you compare multiple isolates, process the **whole cohort with identical versions and thresholds**. For a published analysis, record the [software citations](../CITATION.md) and refer to [validation limitations](validation.md).
