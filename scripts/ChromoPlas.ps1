# ChromoPlas PowerShell launcher: Windows -> WSL2 Ubuntu.
# Analysis tools run in Linux; this is not a native Windows bioinformatics build.
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string] $InputPath,
    [Parameter(Mandatory = $true)][string] $OutputPath,
    [ValidateRange(1, 256)][int] $Threads = 4,
    [string] $Distribution = 'Ubuntu',
    [switch] $DryRun,
    [switch] $KeepGoing
)
$ErrorActionPreference = 'Stop'
if (-not (Get-Command wsl.exe -ErrorAction SilentlyContinue)) {
    throw 'WSL2 is required. See docs/install-windows-powershell.md.'
}
function Convert-ToWslPath {
    param([string] $WindowsPath)
    if ($WindowsPath -notmatch '^[A-Za-z]:\\') {
        throw "Only drive-letter Windows paths are supported: $WindowsPath"
    }
    $value = & wsl.exe --distribution $Distribution --exec wslpath -a -u $WindowsPath
    if ($LASTEXITCODE -ne 0 -or -not $value) {
        throw "WSL could not convert Windows path: $WindowsPath"
    }
    return (($value | Select-Object -Last 1).Trim())
}
$winInput = (Resolve-Path -LiteralPath $InputPath).ProviderPath
$winOutput = (New-Item -ItemType Directory -Path $OutputPath -Force).FullName
$linuxInput = Convert-ToWslPath $winInput
$linuxOutput = Convert-ToWslPath $winOutput

# Shell code is constant. The user paths are separate arguments, not embedded
# into the shell code, so paths with spaces are handled correctly.
$script = @'
set -euo pipefail
conda_binary="$HOME/miniforge3/bin/conda"
if [[ ! -x "$conda_binary" ]]; then
    echo "Miniforge not found inside WSL at ~/miniforge3" >&2
    exit 127
fi
case "$4$5" in
    00) exec "$conda_binary" run --no-capture-output -n chromoplas chromoplas "$1" -o "$2" -t "$3" ;;
    10) exec "$conda_binary" run --no-capture-output -n chromoplas chromoplas "$1" -o "$2" -t "$3" --dry-run ;;
    01) exec "$conda_binary" run --no-capture-output -n chromoplas chromoplas "$1" -o "$2" -t "$3" --keep-going ;;
    11) exec "$conda_binary" run --no-capture-output -n chromoplas chromoplas "$1" -o "$2" -t "$3" --dry-run --keep-going ;;
esac
'@
$dry = if ($DryRun) { '1' } else { '0' }
$keep = if ($KeepGoing) { '1' } else { '0' }
Write-Host "ChromoPlas via WSL2: $winInput -> $winOutput"
& wsl.exe --distribution $Distribution --exec bash -lc $script -- $linuxInput $linuxOutput ([string] $Threads) $dry $keep
if ($LASTEXITCODE -ne 0) {
    throw "ChromoPlas failed in WSL (exit code $LASTEXITCODE); inspect the output above."
}
Write-Host "Report: $winOutput\07_reports\report.html"
