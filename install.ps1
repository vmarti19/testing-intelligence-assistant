param(
    [switch]$Bench
)

function Ensure-Admin {
    if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
        Write-Error "Este script debe ejecutarse como Administrador."
        exit 1
    }
}

function Ensure-Command($cmd, $installAction) {
    if (-not (Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Host "$cmd no encontrado. Instalando..." -ForegroundColor Yellow
        Invoke-Expression $installAction
    } else {
        Write-Host "$cmd ya está instalado." -ForegroundColor Green
    }
}

Ensure-Admin

Write-Host "`n--- Iniciando instalación ---`n" -ForegroundColor Cyan

# Verificar e instalar herramientas necesarias
Ensure-Command "git" 'winget install --id Git.Git -e --source winget'
Ensure-Command "code" 'winget install --id Microsoft.VisualStudioCode -e --source winget'
Ensure-Command "python" 'winget install --id Python.Python.3 -e --source winget'

# Ruta del repositorio
$repoUrl = "https://github.com/vmarti19/visteon-assistant-intelligence.git"
$targetDir = "C:\tia"

# Clonar el repositorio
if (-not (Test-Path $targetDir)) {
    Write-Host "Clonando repositorio en $targetDir..." -ForegroundColor Cyan
    git clone $repoUrl $targetDir
} else {
    Write-Host "El directorio ya existe. Saltando clonación." -ForegroundColor Yellow
}

# Detectar Python
$pythonPath = Get-Command python | Select-Object -ExpandProperty Source
if (-not $pythonPath) {
    Write-Error "Python no está instalado o no está en PATH."
    exit 1
}

# Instalar Poetry si no está presente
try {
    & $pythonPath -m poetry --version > $null 2>&1
} catch {
    Write-Host "Instalando Poetry..." -ForegroundColor Cyan
    (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | & $pythonPath -
    $env:Path += ";$env:USERPROFILE\AppData\Roaming\Python\Scripts"
}

# Configurar entorno virtual en C:\tia\.venv
Set-Location $targetDir
Write-Host "Configurando entorno virtual en C:\tia\.venv..." -ForegroundColor Cyan
& $pythonPath -m poetry config virtualenvs.in-project false
& $pythonPath -m poetry config virtualenvs.path "$targetDir\.venv"

# Instalar dependencias
Write-Host "Instalando dependencias desde pyproject.toml..." -ForegroundColor Cyan
& $pythonPath -m poetry install

# Configuración personalizada
if ($Bench) {
    Write-Host "Configuración para banco de pruebas seleccionada." -ForegroundColor Magenta
    # Agrega aquí configuraciones específicas
} else {
    Write-Host "Configuración personal seleccionada." -ForegroundColor Magenta
}

Write-Host "`n✅ Instalación completada. Reinicia la terminal para aplicar los cambios." -ForegroundColor Green
