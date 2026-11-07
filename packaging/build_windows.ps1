# Build a Windows onedir bundle of RetailPOS with PyInstaller.
# Must be run ON Windows (PyInstaller does not cross-compile).
#
# First-time setup, from the repo root, in PowerShell:
#   py -3.11 -m venv venv
#   venv\Scripts\Activate.ps1
#   pip install -r requirements.txt
#   pip install pyinstaller "kivy_deps.sdl2" "kivy_deps.glew"
#
# Then build:
#   .\packaging\build_windows.ps1

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Split-Path -Parent $ScriptDir
Set-Location $RepoRoot

if (-not (Test-Path "venv")) {
    Write-Error "No venv\ found in $RepoRoot - create one and 'pip install -r requirements.txt' (plus kivy_deps.sdl2/glew and pyinstaller) first."
    exit 1
}

& "venv\Scripts\Activate.ps1"

pip show pyinstaller > $null 2>&1
if ($LASTEXITCODE -ne 0) { pip install pyinstaller }

pip show kivy_deps.sdl2 > $null 2>&1
if ($LASTEXITCODE -ne 0) { pip install "kivy_deps.sdl2" "kivy_deps.glew" }

Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue

pyinstaller packaging\RetailPOS.spec --noconfirm

Write-Host ""
Write-Host "Build complete: $RepoRoot\dist\RetailPOS\"
Write-Host "Run it with: $RepoRoot\dist\RetailPOS\RetailPOS.exe"
Write-Host ""
Write-Host "To hand this to a client, zip the dist\RetailPOS folder, or wrap it with"
Write-Host "Inno Setup (see packaging\README.md) for a proper Windows installer."
