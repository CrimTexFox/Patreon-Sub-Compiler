param([string]$Python = "python")

$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
$workPath = Join-Path $projectRoot ".pyinstaller"

Push-Location $PSScriptRoot
try {
    & $Python -m PyInstaller --clean --noconfirm --distpath (Join-Path $projectRoot "dist") --workpath $workPath ".\PatreonSubCompiler.spec"
    if ($LASTEXITCODE -ne 0) { throw "Executable build failed." }
} finally {
    Pop-Location
}
