$ErrorActionPreference = 'Stop'

$Root = Split-Path -Parent $PSScriptRoot
$Venv = Join-Path $Root '.venv'
$Report = Join-Path $env:TEMP ("DRUMSPLIT_SETUP_{0}.txt" -f (Get-Date -Format 'yyyyMMdd_HHmmss'))

Start-Transcript -Path $Report -Force
try {
    Set-Location $Root

    if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
        throw 'Python Launcher (py.exe) was not found. Install Python 3.10 or 3.11.'
    }

    if (-not (Test-Path $Venv)) {
        py -3.11 -m venv $Venv
    }

    $Python = Join-Path $Venv 'Scripts\python.exe'
    & $Python -m pip install --upgrade pip
    & $Python -m pip install -e '.[dev]'
    & $Python -m drumsplit.setup_model --model-dir (Join-Path $Root 'model')
    & $Python -m ruff check .
    & $Python -m pytest

    Write-Host "DrumSplit setup completed."
    Write-Host "Run: .\.venv\Scripts\drumsplit.exe INPUT OUTPUT"
}
finally {
    Stop-Transcript
    Get-Content $Report | Set-Clipboard
    Write-Host "Report: $Report"
    Write-Host 'Report copied to clipboard.'
}
