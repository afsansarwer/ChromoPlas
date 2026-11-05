# ChromoPlas Desktop for Windows — build and installation guide

**Status: desktop preview, not a validated general-release Windows product.**
The Windows executable, installer and GUI can be built automatically. A live
first-time WSL2 installation and a complete real-genome run must still pass the
acceptance checks below on Windows before calling this release production-ready.

The application keeps the existing ChromoPlas scientific workflow. It adds a
Windows interface and automates the supporting Linux environment. Users do not
install Python, Conda or bioinformatics commands manually.

## What an end user does

1. Download `ChromoPlas-Setup-0.1.0-x64.exe` from the maintainer's verified build.
2. Run the installer and open ChromoPlas from the Start menu.
3. Click **Set up engine** once. Allow Windows' administrator prompt if WSL needs
   enabling. If requested, restart Windows, reopen the app and click the same
   button again. The app will download Ubuntu, the tools and reference databases.
4. Wait for **Analysis engine ready**. Select an assembled FASTA or a folder of
   assemblies, choose the output folder, choose CPU threads and click **Run analysis**.
5. Click **Open report** or **Results folder**. Each run gets a new result folder.

This is a local application. Selecting a FASTA reads it from the user's computer;
it is not uploaded to a server. Setup downloads software and databases. Analyses
can run offline once setup has passed. A GPU is not required.

## Requirements

| Item | Requirement |
| --- | --- |
| Windows | Windows 11 x64, or Windows 10 22H2 build 19045+; not Windows ARM |
| CPU | Intel/AMD x86-64 with virtualization enabled in BIOS/UEFI |
| Permissions | Administrator approval may be needed once to enable Windows features |
| Disk | Setup checks for 25 GiB free on the system/data drive; additional space is needed for results |
| Memory | Peak RAM has not been benchmarked for the desktop build; test representative assemblies before setting a minimum |
| Network | Internet for the initial downloads; proxy-restricted installations need separate testing |
| Input | Assembled `.fa`, `.fna`, `.fasta`, including `.gz`; no raw FASTQ |

The disk allowance is a conservative installation check, not a measured peak
resource requirement. Download size and setup time depend on the current
Conda packages, reference databases and connection speed. Do not promise a fixed
installation time or unlimited batch capacity.

## Easiest way to build the EXE: GitHub Actions

The repository includes `.github/workflows/windows-desktop.yml`. It runs the
build on an actual Windows runner, so the maintainer does not need a Windows
build environment locally.

1. Put this desktop implementation on a branch named `desktop/windows-installer`.
   A push to any `desktop/**` branch triggers the build, including updates to an
   open pull request from that branch. This avoids duplicate Windows builds for
   both the push and pull-request events.
2. Open the repository's **Actions** tab and select **Build Windows desktop installer**.
3. Open the run for your branch and wait for all steps to pass.
4. In **Artifacts**, download **ChromoPlas-Windows-x64-preview**. GitHub requires
   sign-in to download Actions artifacts. This workflow keeps them for 30 days.
5. Extract the downloaded ZIP. It contains the portable `ChromoPlas.exe`, the
   `ChromoPlas-Setup-0.1.0-x64.exe` installer, and SHA-256 checksum files.
6. Perform the real Windows acceptance checks below. After they pass, upload the
   verified installer and checksum to a GitHub Release for durable distribution.

After the workflow is on the default branch, its **Run workflow** button can also
start a build manually. Build automation does not publish a release or merge a PR.

The workflow smoke-tests the frozen GUI, silently installs the generated setup
file into a path containing spaces and smoke-tests the installed GUI. These
checks do **not** install WSL or run a real biological analysis on the runner.

GitHub-hosted build availability is subject to the repository's Actions settings
and current account limits. Use the local method if Actions is unavailable.

## Build it yourself on Windows

Only the person building the application needs these development tools:

- [Python 3.11 x64](https://www.python.org/downloads/windows/), including Tcl/Tk and the Python launcher.
- [Inno Setup 6](https://jrsoftware.org/isdl.php).
- The full repository source including this desktop implementation.

Open Windows PowerShell in the repository root and run:

```powershell
py -3.11 --version
.\desktop\windows\build.ps1
```

If you use a custom Python or Inno Setup installation:

```powershell
.\desktop\windows\build.ps1 `
  -PythonExe 'C:\Path\To\Python311\python.exe' `
  -IsccExe 'C:\Path\To\Inno Setup 6\ISCC.exe'
```

To build only the portable executable, without Inno Setup:

```powershell
.\desktop\windows\build.ps1 -PortableOnly
```

If PowerShell blocks a downloaded script, review its source and verify the
download origin first. On a personally managed machine, `Unblock-File` removes
the Internet-zone mark from that reviewed file; a process-only RemoteSigned
policy can allow local scripts:

```powershell
Unblock-File .\desktop\windows\build.ps1
Set-ExecutionPolicy -Scope Process RemoteSigned
.\desktop\windows\build.ps1
```

On an organization-managed machine, use the approved policy or the GitHub build;
do not try to override administrator restrictions.

The script creates an isolated `.venv-desktop-build`, installs the pinned
packaging requirements, prepares the source payload, runs the desktop tests,
builds the executable, smoke-tests it and compiles the installer. It stops on
any nonzero exit status. Outputs are under `dist\desktop`.

PyInstaller must run on Windows to produce a Windows application. Renaming a
Linux executable to `.exe` or running the packaging command in WSL is not a
Windows build.

## What is installed and how setup recovers

- Windows app: `%LOCALAPPDATA%\Programs\ChromoPlas`.
- Engine/data/log root: `%LOCALAPPDATA%\ChromoPlas`.
- Dedicated WSL2 distribution: `ChromoPlas-Desktop-v1`.
- Linux analysis account: `chromoplas`, with no interactive password setup.
- Linux source and readiness record: `/opt/chromoplas`.
- Conda environment: `/home/chromoplas/miniforge3/envs/chromoplas`.
- Results: the folder selected by the user, with one new subfolder per run.

The app verifies the Canonical Ubuntu image against a pinned SHA-256 checksum
before import and verifies the bundled analysis source before installation.
It checks the registered environment path and ownership marker before modifying
or stopping the environment. It does not adopt, upgrade, or remove an existing
Ubuntu distribution, change another distro's configuration, or run
`wsl --shutdown`.

Downloading the Linux image retries up to three times. Incomplete image downloads
are discarded, and a successfully verified cached image is reused. Setup never
writes a successful readiness record until the installation and database checks
finish. **Repair engine** reruns the installation checks after a failed setup.
An interrupted initial Miniforge directory is retained with an `incomplete` name.

The dedicated environment is initially downloaded automatically; it is not a
hidden copy of the user's current Linux environment. BIOS virtualization,
blocked administrative permissions and corporate network restrictions cannot be
fixed reliably by an application installer. Failures must stay visible.

## Running analyses and interpreting completion

Inputs are copied into a fresh Linux workspace for each run. The app calls the
existing CLI and streams its real stage messages. There is no invented progress
percentage. Inputs must have distinct filenames/sample names.

On completion, the entire result tree is copied into Windows storage. Pipeline
input symlinks are resolved to real files, so the report does not depend on
Windows symlink permissions or a Linux path after export. Results include
`07_reports/report.html`, figure/data subfolders, `analysis.log`, `desktop_run.json`
and the resolved `conda-explicit.txt` tool-package inventory.

When all assemblies fail QC, the GUI says they were excluded and opens the QC
report; it does not claim that gene/plasmid analysis completed successfully.
Ordinary tool failures return an error and preserve logs/partial results.

Successful and QC-excluded runs remove only their own temporary Linux workspace.
Failed or manually stopped jobs retain it for diagnosis. **Stop** terminates only
the dedicated ChromoPlas distribution; partial results may remain in Linux rather
than being exported to Windows. Do not close the application during setup.

## Versions, reproducibility and databases

The desktop bundle includes the analysis source; it does not download arbitrary
new ChromoPlas source on each run. The payload hash is checked against the
installed engine version before analysis.

**Important limitation:** the inherited `INSTALL.sh` resolves compatible Conda
package versions and initializes the upstream databases at setup time. The
initial installation is therefore not a fully locked, reproducible scientific
environment. `Repair engine` can change tools according to that installer.
The resolved Conda package list, ABRicate database list, MOB-suite status and
database file metadata are recorded for auditing. Metadata is not a substitute
for a cryptographic database snapshot.

For a stable public release, install and validate one reference engine, freeze
the Conda environment and database versions, then distribute a versioned engine
snapshot (subject to dependency/database licenses) or a locked installer.
For a personal backup of a validated engine:

```powershell
wsl --terminate ChromoPlas-Desktop-v1
wsl --export ChromoPlas-Desktop-v1 .\ChromoPlas-engine-backup.tar
Get-FileHash .\ChromoPlas-engine-backup.tar -Algorithm SHA256
```

Do not distribute a personal engine export containing genomes, failed jobs or
other private data. Third-party tools and databases retain their own licenses
and citation requirements; the ChromoPlas MIT license does not replace them.

## Acceptance checks before releasing to other researchers

Record Windows version, desktop commit, engine payload hash, tool/database
versions, runtime, peak RAM and available disk for each test.

1. **Clean Windows machine:** no Python, Conda, Ubuntu or WSL. Install, allow the
   Windows feature setup, restart if needed and finish setup through the GUI.
2. **Existing WSL installation:** confirm the user's Ubuntu distributions and
   chosen default are unaffected. Verify `wsl --list --verbose` shows the managed
   ChromoPlas distribution as version 2.
3. **Real biological analysis:** run a real QC-PASS assembled bacterial genome.
   Compare gene detections, localization TSVs and figures with a CLI run using
   the same source, tool versions, databases, thresholds and input.
   The bundled tiny example tests workflow planning; it is not a biological validation dataset.
4. **Paths:** test Windows usernames, input/output paths with spaces, non-ASCII
   characters, and files on a second local drive. Network shares are unsupported.
5. **QC failure:** use an intentionally unsuitable assembly; confirm that the
   GUI reports QC exclusion and that the report explains skipped analyses.
6. **Recovery:** interrupt a download, retry setup, decline the UAC prompt, test
   low disk space, and stop an analysis. Confirm failures cannot report success.
7. **Offline and restart:** restart Windows after setup, disconnect from the
   Internet and run an analysis through the installed GUI.
8. **Uninstall/reinstall:** results remain readable and a reinstalled app can
   validate its existing managed engine. Confirm installer and GUI checks pass
   with normal user permissions.

The generic unit tests and packaging smoke tests are useful but do not replace
these real Windows/WSL checks.

## Uninstall

Windows **Installed apps → ChromoPlas Desktop Preview → Uninstall** removes the
Windows launcher. Results, databases and the managed Linux environment remain
to avoid deleting research data without a separate deliberate action.

To remove the engine as well, first back up results and any failed-job files.
The following command permanently deletes only that distribution and its contents:

```powershell
wsl --unregister ChromoPlas-Desktop-v1
```

After confirming that it is unregistered and your results are backed up, remove
`%LOCALAPPDATA%\ChromoPlas` through File Explorer if desired. Leave other WSL
distributions and Windows features alone.

## Primary technical references

- [Microsoft: WSL installation](https://learn.microsoft.com/en-us/windows/wsl/install).
- [Microsoft: import, export and other WSL commands](https://learn.microsoft.com/en-us/windows/wsl/basic-commands).
- [Canonical: Ubuntu Base images and checksums](https://cdimage.ubuntu.com/ubuntu-base/releases/24.04/release/).
- [PyInstaller manual](https://pyinstaller.org/en/stable/).
- [Inno Setup](https://jrsoftware.org/isinfo.php).
- [GitHub: downloading Actions artifacts](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/download-workflow-artifacts).
