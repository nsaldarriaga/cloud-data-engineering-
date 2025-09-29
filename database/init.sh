#!/bin/bash

# =============================================================================
# Script de Inicialización de Base de Datos
# ITBA - Cloud Data Engineering - Ejercicio 3
# =============================================================================
# Este script ejecuta los archivos SQL para crear la estructura de la base
# de datos PostgreSQL para el proyecto de datos meteorológicos.
# =============================================================================

# Colores para output (opcional, mejora legibilidad)
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# =============================================================================
# Configuración de conexión a PostgreSQL
# =============================================================================
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="weather_db"
DB_USER="weather_user"
DB_PASSWORD="weather_pass"

# Directorio donde están los archivos SQL
SQL_DIR="$(dirname "$0")/sql"

# =============================================================================
# Función para imprimir mensajes
# =============================================================================
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# =============================================================================
# Verificar que PostgreSQL esté corriendo
# =============================================================================
print_message "Verificando conexión a PostgreSQL..."

# Verificar si el contenedor está corriendo
if ! docker ps | grep -q weather_postgres; then
    print_error "El contenedor de PostgreSQL no está corriendo."
    print_message "Ejecuta: docker-compose up -d"
    exit 1
fi

print_message "✓ Contenedor PostgreSQL está corriendo"

# =============================================================================
# Ejecutar scripts SQL
# =============================================================================
print_message "Iniciando creación de tablas..."

# Exportar password para psql (evita prompt interactivo)
export PGPASSWORD=$DB_PASSWORD

# Ejecutar el script SQL de creación de tablas
print_message "Ejecutando: 01_create_tables.sql"

docker exec -i weather_postgres psql \
    -h localhost \
    -U $DB_USER \
    -d $DB_NAME \
    -f /tmp/create_tables.sql \
    < "$SQL_DIR/01_create_tables.sql"

# Verificar si el comando fue exitoso
if [ $? -eq 0 ]; then
    print_message "✓ Tablas creadas exitosamente"
else
    print_error "Error al crear las tablas"
    exit 1
fi

# Limpiar variable de password
unset PGPASSWORD

# =============================================================================
# Verificar estructura creada
# =============================================================================
print_message "Verificando estructura de la base de datos..."

export PGPASSWORD=$DB_PASSWORD

# Listar tablas creadas
print_message "Tablas en la base de datos:"
docker exec -i weather_postgres psql \
    -h localhost \
    -U $DB_USER \
    -d $DB_NAME \
    -c "\dt"

unset PGPASSWORD

# =============================================================================
# Mensaje final
# =============================================================================
echo ""
print_message "=========================================="
print_message "Base de datos inicializada correctamente"
print_message "=========================================="
echo ""
print_message "Próximos pasos:"
echo "  1. Verificar tablas: docker exec -it weather_postgres psql -U weather_user -d weather_db -c '\dt'"
echo "  2. Ver estructura: docker exec -it weather_postgres psql -U weather_user -d weather_db -c '\d+ weather_data'"
echo "  3. Continuar con Ejercicio 4: Cargar datos"
echo ""