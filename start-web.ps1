# start-web.ps1 - PowerShell entrypoint for the web UI on Windows.
# Mirrors start-web.sh; intended to be invoked by start-web.bat or directly.

$ErrorActionPreference = "Stop"

if (-not $env:NLP_SUITE_DIR) {
    $env:NLP_SUITE_DIR = Join-Path $env:USERPROFILE "nlp-suite"
}

# Verify Docker Desktop is running.
try {
    docker info | Out-Null
} catch {
    Write-Host "Docker is not running. Please start Docker Desktop and try again."
    exit 1
}

# Ensure the host data directories exist.
foreach ($sub in @("input", "output", "csvInput")) {
    $path = Join-Path $env:NLP_SUITE_DIR $sub
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
    }
}

# Bring the stack up.
docker compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "docker compose failed. See output above."
    exit 1
}

Write-Host "Waiting for NLP Suite to start..."
$ready = $false
for ($i = 0; $i -lt 60; $i++) {
    try {
        $r = Invoke-WebRequest -Uri "http://localhost:8000" -UseBasicParsing -TimeoutSec 2
        if ($r.StatusCode -eq 200) { $ready = $true; break }
    } catch {
        Start-Sleep -Seconds 1
    }
}

if (-not $ready) {
    Write-Host "NLP Suite did not start within 60 seconds."
    Write-Host "Run 'docker compose logs' to investigate."
    exit 1
}

Write-Host "NLP Suite is running at http://localhost:8000"
Write-Host "Your files are at: $env:NLP_SUITE_DIR"

Start-Process "http://localhost:8000"
