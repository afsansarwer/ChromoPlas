# Windows PowerShell installation (GenomeFlow via WSL2)

**Experimental:** GenomeFlow does **not** include a native Windows build of Prokka, ABRicate or MOB-suite. The provided PowerShell script launches the **Linux GenomeFlow package in Ubuntu under WSL2**. This Windows path has not yet received full end-to-end validation.

## 1. Install WSL2 + Ubuntu

Open **PowerShell as Administrator**:

~~~powershell
wsl --install -d Ubuntu
~~~

Restart if requested. Start Ubuntu from the Windows Start menu and create a Linux username and password. Back in PowerShell:

~~~powershell
wsl --list --verbose
~~~

The Ubuntu distribution should report WSL **version 2**. Its name might be \`Ubuntu-24.04\` instead of \`Ubuntu\`; use that name with the launcher's \`-Distribution\` option.

## 2. Install the actual pipeline inside Ubuntu

Open **Ubuntu** (not PowerShell), then enter:

~~~bash
sudo apt update
sudo apt install -y git curl ca-certificates
curl -fsSLo Miniforge3.sh "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-$(uname -m).sh"
bash Miniforge3.sh -b -p "$HOME/miniforge3"
source "$HOME/miniforge3/etc/profile.d/conda.sh"
git clone https://github.com/afsansarwer/genomeflow.git
cd genomeflow
mamba create -y -n genomeflow -c conda-forge -c bioconda \
  python=3.11 snakemake prokka abricate mob_suite typer pyyaml pip pytest
conda activate genomeflow
python -m pip install --no-deps -e .
genomeflow --help
abricate --list
~~~

Skip the Miniforge installation if it already exists; initialize the installed Conda instead. First-time MOB-suite setup may download large reference datasets.

## 3A. Recommended: run directly in Ubuntu

Copy a real assembled bacterial FASTA to your Ubuntu home folder and run:

~~~bash
genomeflow "$HOME/genome.fna" -o "$HOME/genomeflow-results" -t 4
~~~

For better performance and fewer symlink problems, keep inputs and results **inside WSL2's Linux filesystem**, rather than \`/mnt/c\`. Find outputs from Windows Explorer through \`\\wsl$\Ubuntu\home\<linux-username>\` (adjust distribution name).

## 3B. Optional: run from Windows PowerShell

Clone the repository to **Windows** as well, to obtain \`scripts\GenomeFlow.ps1\`. This second clone does *not* install Prokka or GenomeFlow into Windows: the pipeline executes from your **Ubuntu installation**.

In PowerShell, change to the folder containing the repository, then:

~~~powershell
.\scripts\GenomeFlow.ps1 -InputPath "C:\Users\YOU\Downloads\genome.fna" -OutputPath "C:\Users\YOU\GenomeFlow-results" -Threads 4
~~~

Directory input and dry run:

~~~powershell
.\scripts\GenomeFlow.ps1 -InputPath "C:\Users\YOU\Genomes" -OutputPath "C:\Users\YOU\GenomeFlow-batch" -Threads 8 -DryRun
~~~

If your Ubuntu distribution is named \`Ubuntu-24.04\`, append \`-Distribution "Ubuntu-24.04"\`.

If script execution is blocked, and after reviewing the script, the following adjusts the execution policy for **only your current PowerShell process**:

~~~powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
~~~

**Limitations:** The launcher supports Windows **drive-letter paths** (e.g. \`C:\Data\genome.fna\`) and translates them using WSL's \`wslpath\`; network paths and \`\\wsl$\` paths are not supported by this wrapper. Linux symlinks and filesystem permissions may behave differently on Windows-mounted drives. If this causes errors, run method **3A** inside Ubuntu.

## 4. Open the report

After a completed PowerShell run, open your selected Windows output directory and find \`07_reports\report.html\`.

## Troubleshooting

- WSL not installed: [Microsoft WSL installation](https://learn.microsoft.com/en-us/windows/wsl/install).
- Wrong Ubuntu name: run \`wsl --list --verbose\` and use the correct \`-Distribution\`.
- "Miniforge not found": the launcher expects Ubuntu Miniforge in \`~/miniforge3\`.
- "genomeflow missing": verify package installation and Conda environment **inside Ubuntu**, not Windows.
- Database failures: see [Troubleshooting](troubleshooting.md).

For updating all Linux tools and databases, open Ubuntu/WSL2 and follow [update instructions](updating.md).

See also [command reference](../command_help.md) and [validation notes](validation.md).
