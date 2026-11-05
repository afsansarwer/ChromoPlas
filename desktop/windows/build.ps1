# Run from Windows PowerShell: .\desktop\windows\build.ps1
[CmdletBinding()]
param([string]$PythonExe = "", [string]$IsccExe = "", [switch]$PortableOnly)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
Push-Location $repoRoot
try {
    if (-not $PythonExe) {
        $PythonExe = (& py -3.11 -c 'import sys; print(sys.executable)' | Select-Object -Last 1)
        if ($LASTEXITCODE -ne 0) { throw 'Install 64-bit Python 3.11, including the Python launcher, first.' }
    }
    & $PythonExe -c "import sys, platform; assert sys.platform == 'win32' and platform.machine().lower() in ('amd64','x86_64'), 'Use Windows x64 Python'; assert sys.version_info[:2] == (3,11), 'Use Python 3.11'"
    if ($LASTEXITCODE -ne 0) { throw 'Python platform/version check failed.' }
    if (-not $PortableOnly -and -not $IsccExe) {
        $candidates = @(
            "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
            "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
            "$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe"
        )
        $IsccExe = $candidates | Where-Object { Test-Path $_ } | Select-Object -First 1
        if (-not $IsccExe) {
            $found = Get-Command ISCC.exe -ErrorAction SilentlyContinue
            if ($found) { $IsccExe = $found.Source }
        }
        if (-not $IsccExe) { throw 'Install Inno Setup 6, pass -IsccExe, or use -PortableOnly.' }
    }
    & $PythonExe -m venv .venv-desktop-build
    if ($LASTEXITCODE -ne 0) { throw 'Could not create the isolated build environment.' }
    $buildPython = Join-Path $repoRoot '.venv-desktop-build\Scripts\python.exe'
    & $buildPython -m pip install -r desktop/windows/build-requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'Could not install build dependencies.' }
    & $buildPython desktop/prepare_payload.py
    if ($LASTEXITCODE -ne 0) { throw 'Could not prepare the bundled analysis source.' }
    & $buildPython -m pytest -q tests/test_desktop.py
    if ($LASTEXITCODE -ne 0) { throw 'Desktop tests failed; no installer was produced.' }
    & $buildPython -m PyInstaller --noconfirm --clean --onefile --windowed --noupx `
        --name ChromoPlas --paths . --add-data 'desktop/assets;desktop/assets' `
        --distpath dist/desktop --workpath build/desktop --specpath build desktop/launcher.py
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller failed.' }
    $application = Join-Path $repoRoot 'dist\desktop\ChromoPlas.exe'
    $smoke = Start-Process -FilePath $application -ArgumentList '--smoke-test' -Wait -PassThru
    if ($smoke.ExitCode -ne 0) { throw 'Packaged GUI smoke test failed.' }
    if (-not $PortableOnly) {
        & $IsccExe desktop/windows/ChromoPlas.iss
        if ($LASTEXITCODE -ne 0) { throw 'Inno Setup compilation failed.' }
    }
    Get-ChildItem dist/desktop -Filter *.exe | ForEach-Object {
        $hash = (Get-FileHash -Algorithm SHA256 $_.FullName).Hash.ToLowerInvariant()
        [IO.File]::WriteAllText(($_.FullName + '.sha256'), ($hash + '  ' + $_.Name + "`n"), [Text.Encoding]::ASCII)
    }
    Write-Host 'Build completed. Files are in dist\desktop. Test on a clean Windows PC before distribution.'
} finally {
    Pop-Location
}
