$ErrorActionPreference = "Stop"

$App = Join-Path $PSScriptRoot "auto_clicker.py"

$Python = Get-Command py -ErrorAction SilentlyContinue
if ($Python) {
    & py -3 $App
    exit $LASTEXITCODE
}

$Python = Get-Command python -ErrorAction SilentlyContinue
if ($Python) {
    & python $App
    exit $LASTEXITCODE
}

Write-Error "No Python runtime was found. Install Python 3 from https://www.python.org/downloads/ and ensure it is on PATH."
