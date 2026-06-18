param(
    [switch]$Recreate,
    [switch]$WithQiskit,
    [switch]$WithCloudKit
)

$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$Venv = Join-Path $Root ".venv"
$Python = Join-Path $Venv "Scripts\python.exe"

function Invoke-VenvPython {
    param([string[]]$PythonArgs)
    & $Python @PythonArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed: $Python $($PythonArgs -join ' ')"
    }
}

Push-Location $Root
try {
    $py310Version = (& py -3.10 --version) -join " "
    if ($py310Version -notmatch "3\.10\.11") {
        throw "Expected Python 3.10.11 via py -3.10, got: $py310Version"
    }

    if ($Recreate -and (Test-Path $Venv)) {
        Remove-Item -LiteralPath $Venv -Recurse -Force
    }

    if (-not (Test-Path $Python)) {
        & py -3.10 -m venv .venv
        if ($LASTEXITCODE -ne 0) {
            throw "venv creation failed"
        }
    }

    $venvVersion = (& $Python --version) -join " "
    if ($venvVersion -notmatch "3\.10\.11") {
        throw "Expected .venv Python 3.10.11, got: $venvVersion"
    }

    Invoke-VenvPython @("-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel")
    Invoke-VenvPython @("-m", "pip", "install", "-e", ".[dev]")

    if ($WithQiskit) {
        Invoke-VenvPython @("-m", "pip", "install", "-e", ".[qiskit]")
    }

    if ($WithCloudKit) {
        Invoke-VenvPython @("-m", "pip", "install", "-r", "requirements\local-cloud-kit.txt")
    }

    Invoke-VenvPython @("-m", "pip", "check")
    Invoke-VenvPython @("-m", "pip", "list", "--format=freeze")
}
finally {
    Pop-Location
}
