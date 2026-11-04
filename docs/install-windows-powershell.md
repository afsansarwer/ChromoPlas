# Windows PowerShell installation (ChromoPlas via WSL2)

See the [main installation checklist](../INSTALL.md) for the shared tool requirements and verification steps.

ChromoPlas runs on Windows through **Ubuntu in WSL2**. **Recommended:** run directly from the WSL terminal using `bash INSTALL.sh`, even if your default shell is Zsh. The PowerShell wrapper below is optional.

## Quick path if Ubuntu/WSL2 is already working

In your **WSL Linux terminal** (not PowerShell):


```bash
git clone https://github.com/afsansarwer/ChromoPlas.git
cd ChromoPlas
bash INSTALL.sh
conda activate chromoplas
chromoplas doctor
```

If you have already cloned it, just run \`bash INSTALL.sh\` in the existing clone. The script uses Conda, never requires Mamba, and will not install into \`(base)\`. See [Debian/WSL beginner setup](install-debian.md).

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

## 2. Install ChromoPlas inside Ubuntu

Open the **Ubuntu/WSL terminal** (Bash or Zsh) and enter:


```bash
git clone https://github.com/afsansarwer/ChromoPlas.git
cd ChromoPlas
bash INSTALL.sh
conda activate chromoplas
chromoplas doctor
```

Skip the clone if it already exists. If \`conda activate\` is unavailable, follow the initialization instruction printed by the installer. The script detects existing Conda at nonstandard paths (for example \`~/miniconda3\`).

## 3A. Recommended: run directly in Ubuntu

Copy a real assembled bacterial FASTA to your Ubuntu home folder and run:

~~~bash
chromoplas "$HOME/genome.fna" -o "$HOME/chromoplas-results" -t 4
~~~

For better performance and fewer symlink problems, keep inputs and results **inside WSL2's Linux filesystem**, rather than \`/mnt/c\`. Find outputs from Windows Explorer through \`\\wsl$\Ubuntu\home\<linux-username>\` (adjust distribution name).

## 3B. Optional: run from Windows PowerShell

Clone the repository to **Windows** as well, to obtain \`scripts\ChromoPlas.ps1\`. This second clone does *not* install analysis tools into Windows: the pipeline executes from your **Ubuntu installation**.

In PowerShell, change to the folder containing the repository, then:

~~~powershell
.\scripts\ChromoPlas.ps1 -InputPath "C:\Users\YOU\Downloads\genome.fna" -OutputPath "C:\Users\YOU\ChromoPlas-results" -Threads 4
~~~

Directory input and dry run:

~~~powershell
.\scripts\ChromoPlas.ps1 -InputPath "C:\Users\YOU\Genomes" -OutputPath "C:\Users\YOU\ChromoPlas-batch" -Threads 8 -DryRun
~~~

If your Ubuntu distribution is named \`Ubuntu-24.04\`, append \`-Distribution "Ubuntu-24.04"\`.

If script execution is blocked, and after reviewing the script, the following adjusts the execution policy for **only your current PowerShell process**:

~~~powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
~~~

**Supported paths:** The PowerShell launcher uses Windows **drive-letter paths** (e.g. \`C:\Data\genome.fna\`) and translates them using WSL's \`wslpath\`; network paths and \`\\wsl$\` paths are not supported by this wrapper. Linux symlinks and filesystem permissions may behave differently on Windows-mounted drives. If this causes errors, run method **3A** inside Ubuntu.

## 4. Open the report

After a completed PowerShell run, open your selected Windows output directory and find \`07_reports\report.html\`.

## Troubleshooting

- WSL not installed: [Microsoft WSL installation](https://learn.microsoft.com/en-us/windows/wsl/install).
- Wrong Ubuntu name: run \`wsl --list --verbose\` and use the correct \`-Distribution\`.
- "Miniforge not found": the launcher expects Ubuntu Miniforge in \`~/miniforge3\`.
- "chromoplas missing": verify package installation and Conda environment **inside Ubuntu**, not Windows.
- Database failures: see [Troubleshooting](troubleshooting.md).

For updating all Linux tools and databases, open Ubuntu/WSL2 and follow [update instructions](updating.md).

See also [command reference](../command_help.md) and [validation notes](validation.md).
