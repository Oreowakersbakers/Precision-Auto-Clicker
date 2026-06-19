param(
    [switch]$OneFile
)

$ErrorActionPreference = "Stop"

$RepoRoot = $PSScriptRoot
$SpecPath = Join-Path $RepoRoot "PrecisionAutoClicker.spec"
$BundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

function Resolve-Python {
    if (Test-Path -LiteralPath $BundledPython) {
        return $BundledPython
    }

    $PyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($PyLauncher) {
        return "py -3"
    }

    $Python = Get-Command python -ErrorAction SilentlyContinue
    if ($Python) {
        return "python"
    }

    throw "No Python runtime was found. Install Python 3 or run this from Codex with the bundled runtime available."
}

function Invoke-Python {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Args
    )

    if ($script:PythonCommand -eq $BundledPython) {
        & $script:PythonCommand @Args
        if ($LASTEXITCODE -ne 0) {
            throw "Python command failed with exit code $LASTEXITCODE."
        }
        return
    }

    if ($script:PythonCommand -eq "py -3") {
        & py -3 @Args
        if ($LASTEXITCODE -ne 0) {
            throw "Python command failed with exit code $LASTEXITCODE."
        }
        return
    }

    & python @Args
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed with exit code $LASTEXITCODE."
    }
}

$PythonCommand = Resolve-Python
$script:PythonCommand = $PythonCommand

Write-Host "Using Python: $PythonCommand"

$PyInstallerCheck = $false
try {
    Invoke-Python -Args @(
        "-c",
        "import importlib.util, sys; sys.exit(0 if importlib.util.find_spec('PyInstaller') else 1)"
    ) | Out-Null
    $PyInstallerCheck = $true
} catch {
    $PyInstallerCheck = $false
}

if (-not $PyInstallerCheck) {
    Write-Host "PyInstaller not found. Installing it into the active Python environment..."
    Invoke-Python -Args @("-m", "pip", "install", "pyinstaller")
}

$BuildArgs = @("-m", "PyInstaller", "--noconfirm", "--clean")
if ($OneFile) {
    $BuildArgs += "--onefile"
}
if ($OneFile) {
    $BuildArgs += (Join-Path $RepoRoot "auto_clicker.py")
    $BuildArgs += "--name"
    $BuildArgs += "Precision Auto Clicker"
    $BuildArgs += "--windowed"
} else {
    $BuildArgs += $SpecPath
}

Invoke-Python -Args $BuildArgs

if ($OneFile) {
    $OutputPath = Join-Path $RepoRoot "dist\Precision Auto Clicker.exe"
} else {
    $OutputPath = Join-Path $RepoRoot "dist\Precision Auto Clicker\Precision Auto Clicker.exe"
}

Write-Host ""
Write-Host "Build complete:"
Write-Host $OutputPath
