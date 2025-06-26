param(
    [switch]$Bench
)

function Ensure-Admin {
    if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
        Write-Error "This script must be run as Administrator."
        exit 1
    }
}

function Ensure-Command($cmd, $installAction) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Host "$cmd not found. Installing..." -ForegroundColor Yellow
        Invoke-Expression $installAction
    } else {
        Write-Host "$cmd is already installed." -ForegroundColor Green
    }
}

Ensure-Admin

Write-Host "`n--- Starting installation ---`n" -ForegroundColor Cyan

# Check and install required tools
Ensure-Command "git" 'winget install --id Git.Git -e --source winget'
Ensure-Command "code" 'winget install --id Microsoft.VisualStudioCode -e --source winget'
Ensure-Command "python" 'winget install --id Python.Python.3 -e --source winget'

# Repository path
$repoUrl = "https://github.com/vmarti19/testing-intelligence-assistant.git"
$targetDir = "C:\tia"

# Clone the repository
if (-not (Test-Path $targetDir)) {
    Write-Host "Cloning repository into $targetDir..." -ForegroundColor Cyan
    git clone $repoUrl $targetDir
} else {
    Write-Host "Directory already exists. Skipping clone." -ForegroundColor Yellow
}

# Detect Python
$pythonPath = Get-Command python | Select-Object -ExpandProperty Source
if (-not $pythonPath) {
    Write-Error "Python is not installed or not in PATH."
    exit 1
}

# Check and install Poetry if needed
if (-not (Get-Command poetry -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Poetry..." -ForegroundColor Cyan
    (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
    $env:Path += ";$env:USERPROFILE\AppData\Roaming\Python\Scripts"
    $env:Path += ";$env:APPDATA\Python\Scripts"
}

# Detect Poetry path
$poetryPath = "$env:USERPROFILE\AppData\Roaming\Python\Scripts\poetry.exe"
if (-not (Test-Path $poetryPath)) {
    $poetryPath = "$env:APPDATA\Python\Scripts\poetry.exe"
}

if (-not (Test-Path $poetryPath)) {
    Write-Error "Poetry was not installed correctly. Please restart the terminal or install it manually with 'pip install poetry'."
    exit 1
}

# Configure virtual environment in C:\tia\.venv
Set-Location $targetDir
Write-Host "Configuring virtual environment in C:\tia\.venv..." -ForegroundColor Cyan
& $poetryPath config virtualenvs.in-project false
& $poetryPath config virtualenvs.path "$targetDir\.venv"

# Install dependencies
Write-Host "Installing dependencies from pyproject.toml..." -ForegroundColor Cyan
& $poetryPath install

# Custom configuration
if ($Bench) {
    Write-Host "Test bench configuration selected." -ForegroundColor Magenta
    # Add specific configurations here
} else {
    Write-Host "Personal configuration selected." -ForegroundColor Magenta
}

Write-Host "`n✅ Installation completed. Restart the terminal to apply the changes." -ForegroundColor Green
