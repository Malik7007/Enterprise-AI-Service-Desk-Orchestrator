# Enterprise AI Service Desk - Setup & Run Script
# This script automates venv creation, dependency installation, and concurrent execution.

if (!(Test-Path "venv")) {
    Write-Host "Step 1/3: Creating Python Virtual Environment..." -ForegroundColor Cyan
    python -m venv venv
}
else {
    Write-Host "Step 1/3: Virtual environment already exists. Skipping creation." -ForegroundColor Gray
}

Write-Host "Step 2/3: Syncing Python dependencies..." -ForegroundColor Cyan
./venv/Scripts/python -m pip install --upgrade pip
./venv/Scripts/python -m pip install -r requirements.txt

Write-Host "Step 3/3: Syncing Frontend dependencies..." -ForegroundColor Cyan
Set-Location frontend
npm install
Set-Location ..

Write-Host "`n🚀 Launching Enterprise AI Orchestrator Cluster..." -ForegroundColor Green
Write-Host "--------------------------------------------------" -ForegroundColor Gray
Write-Host "Backend API: http://localhost:8000" -ForegroundColor Blue
Write-Host "Frontend UI: http://localhost:3000" -ForegroundColor DarkMagenta
Write-Host "--------------------------------------------------`n" -ForegroundColor Gray

# Start the Backend in a separate process window
$BackendCmd = "`$env:PYTHONPATH = '$PWD'; & './venv/Scripts/python' 'api/main.py'"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "$BackendCmd"

# Start the Frontend in the current terminal (force port 3000)
npm run dev --prefix frontend -- --port 3000 --strictPort
