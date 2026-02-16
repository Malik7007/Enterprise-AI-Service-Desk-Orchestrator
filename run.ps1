# Enterprise AI Service Desk - High-Speed Runner
Stop-Process -Name python -Force -ErrorAction SilentlyContinue
Stop-Process -Name node -Force -ErrorAction SilentlyContinue

Write-Host '🚀 Launching Cluster...' -ForegroundColor Green

# Ensure we are in the root directory relative to this script
$ScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptRoot
$ROOT_DIR = $ScriptRoot

$PYTHON_EXE = "$ROOT_DIR\venv\Scripts\python.exe"
$BACKEND_SCRIPT = "$ROOT_DIR\api\main.py"

# Verify virtual environment exists
if (-not (Test-Path $PYTHON_EXE)) {
    Write-Error "Virtual environment not found at $PYTHON_EXE. Please run 'python -m venv venv' first."
    exit 1
}

# Start Backend
$BACKEND_CMD = "`$env:PYTHONPATH = '$ROOT_DIR'; & '$PYTHON_EXE' '$BACKEND_SCRIPT'"
Start-Process powershell -ArgumentList '-NoExit', '-Command', $BACKEND_CMD

# Start Frontend
if (Test-Path "frontend") {
    Set-Location frontend
    npm run dev -- --port 3000
}
else {
    Write-Error "Frontend directory not found!"
}
