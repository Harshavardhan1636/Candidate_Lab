$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
    python -m venv .venv
    & '.venv\Scripts\python.exe' -m pip install -r requirements.txt
}
if (-not (Test-Path -LiteralPath 'dist\index.html')) {
    npm.cmd ci
    npm.cmd run build
}
$env:DEMO_MODE = '1'
if (-not $env:SEMANTIC_MODEL_PATH -and (Test-Path -LiteralPath 'models\all-MiniLM-L6-v2\model.safetensors')) {
    $env:SEMANTIC_MODEL_PATH = Join-Path $PSScriptRoot 'models\all-MiniLM-L6-v2'
}
$env:HF_HUB_OFFLINE = '1'
$env:HF_HOME = Join-Path $PSScriptRoot 'models\.hf'
Write-Host 'Candidate Lab: http://127.0.0.1:8000'
Write-Host 'Local synthetic demo. Recruiter: recruiter@demo.test / RecruiterDemo!2026'
Write-Host 'Auditor: auditor@demo.test / AuditorDemo!2026'
& '.venv\Scripts\python.exe' -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
