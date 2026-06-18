$ErrorActionPreference = "Stop"

$BundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$App = Join-Path $PSScriptRoot "auto_clicker.py"

if (Test-Path -LiteralPath $BundledPython) {
    & $BundledPython $App
    exit $LASTEXITCODE
}

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

Write-Error "No Python runtime was found. Install Python 3 or run this from Codex with the bundled runtime available."
