# Troubleshooting ChromoPlas

## Command not found or wrong Python

Activate your intended Conda environment before installing or running:

~~~bash
source "$HOME/miniforge3/etc/profile.d/conda.sh"
conda activate chromoplas
which python chromoplas snakemake abricate mob_recon
~~~

If `chromoplas` is missing, from the GitHub repository root run `python -m pip install --no-deps -e .`. This assumes dependencies were installed with Mamba.

## Missing `typer`, `yaml` or `snakemake`

Verify `which python` points inside the **chromoplas** environment. Install Python dependencies into that environment:

~~~bash
mamba install -n chromoplas -c conda-forge typer pyyaml snakemake
~~~

## First dry-run has only 1–3 jobs

The `select_hq` Snakemake **checkpoint** filters FASTA assemblies based on quality metrics. Snakemake dynamically expands dependent jobs only after that checkpoint executes. A short initial dry-run is not itself an error.

## "No FASTA files found"

Input must be assembled bacterial nucleotide FASTA (`.fna`, `.fa`, `.fasta`, or compressed `.gz` variants). Check directory paths and extensions. FASTQ reads are not supported. Avoid duplicate sample names.

## ABRicate missing database

~~~bash
abricate --list
~~~

Default databases are **resfinder**, **vfdb**, **plasmidfinder**. Reference data are **not bundled**. Database setup/versioning may vary by ABRicate version; consult [upstream ABRicate](https://github.com/tseemann/abricate) for `abricate-get_db` and `abricate --setupdb` procedures.

## MOB-suite database setup failed

MOB-suite initialization may download hundreds of MB. Confirm internet access, enough free disk space and database initialization, consulting [upstream MOB-suite](https://github.com/phac-nml/mob-suite). The presence of a `mob_recon` executable does not prove database availability.

## Optional annotation

Prokka can be enabled through the YAML configuration after installing it in the ChromoPlas environment.

## Interrupted workflow

Rerun the **same command** with the same input and output directory. Snakemake usually resumes completed steps. Preserve the `.snakemake/` folder and examine logs under `results/.snakemake/log/`. Start a new output directory for an unrelated cohort.

## Windows PowerShell

PowerShell is only a frontend to Ubuntu under WSL2. Use [Windows setup](install-windows-powershell.md) and confirm Miniforge exists at `~/miniforge3` **inside Ubuntu**. Windows-mounted NTFS drives can be slower or behave differently with symlinks; consider running inside the Linux filesystem.

## Keeping tools and databases updated

Use [the update-all guide](updating.md). Record versions before updates and avoid changing tools/databases halfway through a study.

## Report an issue

[Open a GitHub issue](https://github.com/afsansarwer/genomeflow/issues) including OS and CPU architecture, exact command, relevant error and software/database versions. Never upload confidential biological data or personal identifying metadata.
