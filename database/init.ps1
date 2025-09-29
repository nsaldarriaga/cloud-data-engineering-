# =============================================================================
# Script de Inicialización de Base de Datos (PowerShell)
# ITBA - Cloud Data Engineering - Ejercicio 3
# =============================================================================
# Este script ejecuta los archivos SQL para crear la estructura de la base
# de datos PostgreSQL para el proyecto de datos meteorológicos.
# Versión para Windows PowerShell
# =============================================================================

# Configuración de conexión a PostgreSQL
$DB_HOST = "localhost"
$DB_PORT = "5432"
$DB_NAME = "weather_db"
$DB_USER = "weather_user"
$DB_PASSWORD = "weather_pass"

# Directorio donde están los archivos SQL
$SQL_DIR = Join-Path $PSScriptRoot "sql"
$SQL_FILE = Join-Path $SQL_DIR "01_create_tables.sql"

# =============================================================================
# Funciones de utilidad
# =============================================================================
function Write-Success {
    param($Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Error-Message {
    param($Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Warning-Message {
    param($Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

# =============================================================================
# Verificar que PostgreSQL esté corriendo
# =============================================================================
Write-Success "Verificando conexión a PostgreSQL..."

$container = docker ps --filter "name=weather_postgres" --format "{{.Names}}"

if (-not $container) {
    Write-Error-Message "El contenedor de PostgreSQL no está corriendo."
    Write-Success "Ejecuta: docker-compose up -d"
    exit 1
}

Write-Success "✓ Contenedor PostgreSQL está corriendo"

# =============================================================================
# Ejecutar scripts SQL
# =============================================================================
Write-Success "Iniciando creación de tablas..."

# Leer el contenido del archivo SQL
$sqlContent = Get-Content $SQL_FILE -Raw

# Ejecutar SQL usando docker exec
Write-Success "Ejecutando: 01_create_tables.sql"

$env:PGPASSWORD = $DB_PASSWORD

# Opción 1: Usar pipe con docker exec
$result = $sqlContent | docker exec -i weather_postgres psql `
    -h localhost `
    -U $DB_USER `
    -d $DB_NAME 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Success "✓ Tablas creadas exitosamente"
}
else {
    Write-Error-Message "Error al crear las tablas"
    Write-Host $result
    exit 1
}

# Limpiar variable de password
Remove-Item Env:\PGPASSWORD

# =============================================================================
# Verificar estructura creada
# =============================================================================
Write-Success "Verificando estructura de la base de datos..."

$env:PGPASSWORD = $DB_PASSWORD

Write-Success "Tablas en la base de datos:"
docker exec -i weather_postgres psql `
    -h localhost `
    -U $DB_USER `
    -d $DB_NAME `
    -c "\dt"

Remove-Item Env:\PGPASSWORD

# =============================================================================
# Mensaje final
# =============================================================================
Write-Host ""
Write-Success "=========================================="
Write-Success "Base de datos inicializada correctamente"
Write-Success "=========================================="
Write-Host ""
Write-Success "Próximos pasos:"
Write-Host "  1. Verificar tablas: docker exec -it weather_postgres psql -U weather_user -d weather_db -c '\dt'"
Write-Host "  2. Ver estructura: docker exec -it weather_postgres psql -U weather_user -d weather_db -c '\d+ weather_data'"
Write-Host "  3. Continuar con Ejercicio 4: Cargar datos"
Write-Host ""