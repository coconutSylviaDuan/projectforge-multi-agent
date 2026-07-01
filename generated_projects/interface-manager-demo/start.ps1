$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = "C:\Users\95853\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if (!(Test-Path $Python)) {
  $Python = "python"
}

$Backend = Join-Path $Root "backend"
$Frontend = Join-Path $Root "frontend"

Write-Host "Starting backend on http://localhost:8000"
Start-Process -FilePath $Python -ArgumentList "-m uvicorn main:app --host 127.0.0.1 --port 8000" -WorkingDirectory $Backend

Write-Host "Starting frontend proxy on http://localhost:5173"
Start-Process -FilePath $Python -ArgumentList "dev_proxy.py" -WorkingDirectory $Frontend

Write-Host "Backend:  http://localhost:8000"
Write-Host "Frontend: http://localhost:5173"
Write-Host "Proxy:    http://localhost:5173/api -> http://localhost:8000/api"
