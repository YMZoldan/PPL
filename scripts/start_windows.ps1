param(
    [switch]$Dev
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    Write-Host "Python Launcher (py) not found. Install Python 3.11+ from https://www.python.org/downloads/windows/" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..."
    py -3 -m venv .venv
}

Write-Host "Activating virtual environment and upgrading pip..."
& .\.venv\Scripts\python.exe -m pip install --upgrade pip

Write-Host "Installing project dependencies..."
& .\.venv\Scripts\python.exe -m pip install -e .

if ($Dev) {
    Write-Host "Installing development dependencies..."
    & .\.venv\Scripts\python.exe -m pip install -e .[dev]
}

Write-Host "Starting API on http://127.0.0.1:8000"
& .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
