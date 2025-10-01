# ============================================================================
# SETUP COMPLETO DEL PROYECTO - CLOUD DATA ENGINEERING
# ============================================================================
# Este script automatiza todo el proceso de configuracion del proyecto
# desde cero, simulando la experiencia del profesor al clonar el repo.
# ============================================================================

Write-Host "
===============================================================================
                   CLOUD DATA ENGINEERING - ITBA                          
                    Setup Automatizado del Proyecto                       
===============================================================================
" -ForegroundColor Cyan

$ErrorActionPreference = "Stop"
$TotalSteps = 8  
$CurrentStep = 0

# Funcion para mostrar progreso
function Show-Progress {
    param($Message)
    $script:CurrentStep++
    Write-Host "`n[$script:CurrentStep/$TotalSteps] $Message" -ForegroundColor Yellow
    Write-Host ("=" * 80) -ForegroundColor DarkGray
}

# Funcion para verificar errores
function Test-LastCommand {
    param($ErrorMessage)
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: $ErrorMessage" -ForegroundColor Red
        exit 1
    }
}

# ============================================================================
# PASO 1: Levantar PostgreSQL
# ============================================================================
Show-Progress "Iniciando PostgreSQL con Docker Compose"

if (Test-Path "docker-compose.yml") {
    docker-compose up -d
    Test-LastCommand "No se pudo iniciar PostgreSQL"
    Write-Host "PostgreSQL iniciado correctamente" -ForegroundColor Green
    
    Write-Host "`nEsperando a que PostgreSQL este listo (30 segundos)..." -ForegroundColor Gray
    Start-Sleep -Seconds 30
} else {
    Write-Host "ERROR: No se encontro docker-compose.yml" -ForegroundColor Red
    exit 1
}

# ============================================================================
# PASO 2: Verificar que PostgreSQL este corriendo
# ============================================================================
Show-Progress "Verificando estado de PostgreSQL"

$containers = docker ps --filter "name=weather_postgres" --format "{{.Names}}"
if ($containers -match "weather_postgres") {
    Write-Host "Container 'weather_postgres' esta corriendo" -ForegroundColor Green
} else {
    Write-Host "ERROR: Container de PostgreSQL no esta corriendo" -ForegroundColor Red
    Write-Host "Ejecuta: docker ps -a para mas detalles" -ForegroundColor Yellow
    exit 1
}

# ============================================================================
# PASO 3: Crear las tablas (DDL)
# ============================================================================
Show-Progress "Creando tablas en la base de datos"

if (Test-Path "database\sql\01_create_tables.sql") {
    Get-Content .\database\sql\01_create_tables.sql | docker exec -i weather_postgres psql -U weather_user -d weather_db
    Test-LastCommand "No se pudieron crear las tablas"
    Write-Host "Tablas creadas exitosamente" -ForegroundColor Green
} else {
    Write-Host "ERROR: No se encontro el archivo 01_create_tables.sql" -ForegroundColor Red
    exit 1
}

# ============================================================================
# PASO 4: Construir imagen del Data Loader
# ============================================================================
Show-Progress "Construyendo imagen Docker: weather-data-loader"

if (Test-Path "database\loader\Dockerfile") {
    docker build -t weather-data-loader .\database\loader
    Test-LastCommand "No se pudo construir la imagen weather-data-loader"
    Write-Host "Imagen weather-data-loader construida" -ForegroundColor Green
} else {
    Write-Host "ERROR: No se encontro database\loader\Dockerfile" -ForegroundColor Red
    exit 1
}

# ============================================================================
# PASO 5: Cargar datos en la base de datos
# ============================================================================
Show-Progress "Cargando datos desde archivos JSON"

if (Test-Path "data\raw") {
    $jsonFiles = Get-ChildItem "data\raw" -Filter "*.json"
    Write-Host "Archivos JSON encontrados: $($jsonFiles.Count)" -ForegroundColor Gray
    
    docker run --rm --network host -v ${PWD}/data:/data weather-data-loader
    Test-LastCommand "No se pudieron cargar los datos"
    Write-Host "Datos cargados exitosamente" -ForegroundColor Green
} else {
    Write-Host "ERROR: No se encontro la carpeta data\raw con archivos JSON" -ForegroundColor Red
    exit 1
}

# ============================================================================
# PASO 6: Construir imagen del Reporter
# ============================================================================
Show-Progress "Construyendo imagen Docker: weather-reporter"

if (Test-Path "database\reporter\Dockerfile") {
    docker build -t weather-reporter .\database\reporter
    Test-LastCommand "No se pudo construir la imagen weather-reporter"
    Write-Host "Imagen weather-reporter construida" -ForegroundColor Green
} else {
    Write-Host "ERROR: No se encontro database\reporter\Dockerfile" -ForegroundColor Red
    exit 1
}

# ============================================================================
# PASO 7: Verificar datos cargados
# ============================================================================
Show-Progress "Verificando datos en la base de datos"

Write-Host "`nConsultando cantidad de registros..." -ForegroundColor Gray
$result = docker exec weather_postgres psql -U weather_user -d weather_db -t -c "SELECT COUNT(*) FROM weather_data;"
$recordCount = $result.Trim()

if ($recordCount -gt 0) {
    Write-Host "Base de datos poblada correctamente: $recordCount registros" -ForegroundColor Green
} else {
    Write-Host "ADVERTENCIA: No se encontraron datos en weather_data" -ForegroundColor Yellow
}

# ============================================================================
# PASO 8: Generar Reporte (NUEVO)
# ============================================================================
Show-Progress "Generando reporte de analisis meteorologico"

Write-Host "`nEjecutando consultas SQL y generando reporte...`n" -ForegroundColor Gray
docker run --rm --network host weather-reporter

Write-Host "`nReporte generado exitosamente" -ForegroundColor Green

# ============================================================================
# RESUMEN FINAL
# ============================================================================
Write-Host "
===============================================================================
                          SETUP COMPLETADO                                
===============================================================================
" -ForegroundColor Green

Write-Host "RESUMEN:" -ForegroundColor Cyan
Write-Host "  - PostgreSQL corriendo en puerto 5432" -ForegroundColor Green
Write-Host "  - Tablas creadas (locations, weather_data)" -ForegroundColor Green
Write-Host "  - Datos cargados: $recordCount registros" -ForegroundColor Green
Write-Host "  - Imagenes Docker listas (loader, reporter)" -ForegroundColor Green
Write-Host "  - Reporte de analisis generado" -ForegroundColor Green

Write-Host "`n$('=' * 80)" -ForegroundColor DarkGray
Write-Host ""