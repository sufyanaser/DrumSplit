$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$Report = Join-Path $env:TEMP "DRUMSPLIT_BUILD_$Stamp.txt"

Start-Transcript -Path $Report -Force
try {
    Set-Location $ProjectRoot

    if (-not (Test-Path '.venv\Scripts\python.exe')) {
        py -3.11 -m venv .venv
    }

    & .\.venv\Scripts\python.exe -m pip install --upgrade pip
    & .\.venv\Scripts\python.exe -m pip install -e ".[dev]"

    & .\.venv\Scripts\python.exe -m ruff check .
    & .\.venv\Scripts\python.exe -m pytest -q

    Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue

    & .\.venv\Scripts\python.exe -m PyInstaller `
        --noconfirm `
        --clean `
        --windowed `
        --onedir `
        --name DrumSplit `
        --collect-all demucs `
        --collect-all torch `
        --collect-all torchaudio `
        --collect-all soundfile `
        --hidden-import drumsplit.gui `
        src\drumsplit\gui.py

    if (-not (Test-Path 'dist\DrumSplit\DrumSplit.exe')) {
        throw 'Build completed without dist\DrumSplit\DrumSplit.exe.'
    }

    Compress-Archive `
        -Path 'dist\DrumSplit\*' `
        -DestinationPath 'dist\DrumSplit-Windows-x64.zip' `
        -Force

    Write-Host "BUILD_OK: $ProjectRoot\dist\DrumSplit\DrumSplit.exe"
    Write-Host "ZIP_OK: $ProjectRoot\dist\DrumSplit-Windows-x64.zip"
}
finally {
    Stop-Transcript
    Get-Content $Report -Raw | Set-Clipboard
    Write-Host "REPORT: $Report"
}
