# TP Final - Fundación de Cloud Data Engeneering - ITBA

Weather Data Collection Pipeline
ITBA - Cloud Data Engineering - Trabajo Práctico Final

Pipeline automatizado para recolección y procesamiento de datos meteorológicos desde OpenMeteo API con almacenamiento en PostgreSQL.

# 📁 Estructura del Proyecto

├── weather_data_collector/     # Módulo principal
│   ├── __init__.py
│   ├── api_client.py          # Cliente de API OpenMeteo
│   ├── config.py              # Configuraciones
│   └── utils.py               # Utilidades de datos
├── scripts/
│   ├── __init__.py
│   └── main.py                # Script principal de ejecución
├── test/
│   ├── __init__.py
│   ├── test_config.py         # Tests de configuración
│   └── test_utils.py          # Tests de utilidades
├── data/
│   ├── raw/                   # Datos JSON originales
|   ├──DATASET_DESCRIPTION.md     # Descripción del dataset y preguntas de negocio  
├── docker-compose.yml         # Configuración de PostgreSQL
├── database/
│   ├──init.ps1
│   ├──init.sh
│   └──sql/
|   ├── 01_create_tables.sql
├── requirements.txt
├── .gitignore
└── README.md

# 🚀 Instalación
1. Clonar el Repositorio
git clone https://github.com/nsaldarriaga/cloud-data-engineering-.git
cd cloud-data-engineering-

2. Instalar Dependencias Python
pip install -r requirements.txt

3. Levantar Base de Datos PostgreSQL (Docker)
Requisito: Tener Docker Desktop instalado.

# Levantar contenedor de PostgreSQL
docker-compose up -d

# Verificar que esté corriendo
docker-compose ps

#  Resultado esperado:
NAME               STATUS                    PORTS
weather_postgres   Up X seconds (healthy)   0.0.0.0:5432->5432/tcp

#  🗄️ Configuración de la Base de Datos

El contenedor PostgreSQL se crea automáticamente con las siguientes credenciales:
Parámetro Valor
Host      localhost
Puerto    5432
Base de Datos weather_db
Usuario   weather_user
Contraseña  weather_pass

# Estructura de Tablas
El proyecto utiliza dos tablas principales:
## locations - Ubicaciones meteorológicas

- id (PK) - Identificador único
- location_name - Nombre de la ubicación (iowa_center, illinois_center)
- created_at - Timestamp de creación

## weather_data - Datos meteorológicos (históricos y pronósticos)

-  id (PK) - Identificador único
- location_id (FK) - Referencia a locations
- date - Fecha del registro
- data_type - Tipo de dato ('historical' o 'forecast')
- weather_code - Código WMO del clima
- temperature_2m_max - Temperatura máxima (°C)
- temperature_2m_min - Temperatura mínima (°C)
- daylight_duration - Duración de luz diurna (segundos)
- shortwave_radiation_sum - Radiación de onda corta
- precipitation_sum - Precipitación total (mm)
- et0_fao_evapotranspiration - Evapotranspiración de referencia
- soil_moisture_0_to_100cm_mean - Humedad del suelo
- vapour_pressure_deficit_max - Déficit de presión de vapor
- created_at - Timestamp de creación

# Crear Tablas en la Base de Datos
### Ejecutar script de inicialización (PowerShell)
Get-Content .\database\sql\01_create_tables.sql | docker exec -i weather_postgres psql -U weather_user -d weather_db

### O usando Git Bash
database/init.sh

# Verificar Estructura
### Ver tablas creadas
docker exec -it weather_postgres psql -U weather_user -d weather_db -c "\dt"

# Ver estructura de weather_data
docker exec -it weather_postgres psql -U weather_user -d weather_db -c "\d weather_data"

# Ver estructura de locations
docker exec -it weather_postgres psql -U weather_user -d weather_db -c "\d locations"

#  Conectarse a PostgreSQL
Desde la línea de comandos:
docker-compose exec postgres psql -U weather_user -d weather_db

#  💻 Uso del Pipeline
Ejecutar Pipeline Completo
python -m scripts.main

#  Opciones de Ejecución

# Solo datos históricos
python -m scripts.main --skip-forecast

# Solo pronósticos
python -m scripts.main --skip-historical

# Ver todas las opciones
python -m scripts.main --help

#  📊 Datos Generados

El pipeline genera archivos JSON en data/raw/:
historical_<location>_<date>.json - Datos históricos (2020-2025)
forecast_<location>_<date>.json - Pronósticos (7 días)
combined_<location>_<date>.json - Datos combinados


#  🧪 Testing
# Ejecutar todos los tests
python -m pytest test/ -v

# Ejecutar tests específicos
python -m pytest test/test_config.py -v

#  🐳 Comandos Docker Útiles

# Ver logs de PostgreSQL
docker-compose logs -f postgres

# Detener el contenedor
docker-compose stop

# Iniciar el contenedor
docker-compose start

# Detener y eliminar (los datos persisten en el volumen)
docker-compose down

# Ver estado del contenedor
docker-compose ps

#  📚 Dataset
Para información detallada sobre el dataset y preguntas de negocio, ver DATASET_DESCRIPTION.md.

#  🛠️ Tecnologías Utilizadas

Python 3.7+ - Lenguaje principal
OpenMeteo API - Fuente de datos meteorológicos
PostgreSQL 12.7 - Base de datos relacional
Docker & Docker Compose - Contenedorización
pandas - Procesamiento de datos
pytest - Testing
requests-cache - Caching de API calls


#  🔧 Troubleshooting
Error: Puerto 5432 ya en uso
Si ves el error # Bind for 0.0.0.0:5432 failed: port is already allocated:

# Ver qué está usando el puerto
netstat -ano | findstr :5432

# Detener PostgreSQL local si está instalado
Stop-Service -Name "postgresql-x64-XX"

# O cambiar el puerto en docker-compose.yml
ports:
  - "5433:5432"   # Usar puerto 5433 en lugar de 5432

Contenedor no inicia

# Ver logs para diagnosticar
docker-compose logs postgres

# Recrear el contenedor
docker-compose down
docker-compose up -d