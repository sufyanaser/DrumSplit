# DrumSplit

DrumSplit is a Windows-compatible local wrapper around the open-source `inagoy/drumsep` Hybrid Demucs model.

## Verified engine scope

The upstream model accepts a **drum-only recording** and exports exactly four synchronized stems:

- `kick.wav`
- `snare.wav`
- `cymbals.wav`
- `toms.wav`

It does **not** natively export separate hi-hat, ride, crash, clap, or percussion stems. Those require a different validated model and are outside the current engine scope.

## Supported input

- WAV
- MP3
- FLAC
- OGG
- One file or a directory of files

## Windows setup

Requirements:

- Windows 10 or 11
- Python 3.11
- NVIDIA GPU recommended; CPU fallback is supported
- FFmpeg available to Demucs for compressed formats

Run PowerShell from the repository root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1
```

The setup script:

1. Creates `.venv`.
2. Installs DrumSplit, Demucs, and development checks.
3. Downloads the original upstream checkpoint into `model/`.
4. Runs Ruff and Pytest.
5. Writes a transcript to `%TEMP%` and copies it to the clipboard.

## Usage

```powershell
.\.venv\Scripts\drumsplit.exe "D:\Audio\drums.wav" "D:\Audio\DrumSplit Output"
```

Choose processing device explicitly when required:

```powershell
.\.venv\Scripts\drumsplit.exe input.wav outputs --device cuda
.\.venv\Scripts\drumsplit.exe input.wav outputs --device cpu
```

Output structure:

```text
DrumSplit Output/
└── drums/
    ├── kick.wav
    ├── snare.wav
    ├── cymbals.wav
    └── toms.wav
```

## Machine-readable reporting

The CLI writes JSON Lines events for:

- environment and selected device
- file start/completion
- Demucs engine logs
- stem validation
- actionable errors

This output is suitable for a later desktop interface.

## Validation

Before a change is accepted:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest
```

GitHub Actions runs the same validation on `develop` and `main`.

## Current status

Phase 1 implements the local Python inference layer, model bootstrap, Windows setup, JSONL reporting, stem normalization, duration validation, tests, and CI.

A desktop interface and packaged EXE belong to the next phase after the inference path is verified locally with the actual checkpoint and a drum-only WAV.
