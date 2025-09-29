# TP Final - Fundación de Cloud Data Engeneering - ITBA

Weather Data Collection Pipeline
ITBA - Cloud Data Engineering - Trabajo Práctico Final

Pipeline automatizado para recolección y procesamiento de datos meteorológicos desde OpenMeteo API con almacenamiento en PostgreSQL.

📁 Estructura del Proyecto
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
│   └── processed/             # Datos procesados (futuro)
├── docker-compose.yml         # Configuración de PostgreSQL
├── DATASET_DESCRIPTION.md     # Descripción del dataset y preguntas de negocio
├── requirements.txt
├── .gitignore
└── README.md

🚀 Instalación
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

Resultado esperado:
NAME               STATUS                    PORTS
weather_postgres   Up X seconds (healthy)   0.0.0.0:5432->5432/tcp

🗄️ Configuración de la Base de Datos

El contenedor PostgreSQL se crea automáticamente con las siguientes credenciales:
Parámetro Valor
Host      localhost
Puerto    5432
Base de Datos weather_db
Usuario   weather_user
Contraseña  weather_pass

Conectarse a PostgreSQL
Desde la línea de comandos:
docker-compose exec postgres psql -U weather_user -d weather_db

💻 Uso del Pipeline
Ejecutar Pipeline Completo
python -m scripts.main

Opciones de Ejecución

# Solo datos históricos
python -m scripts.main --skip-forecast

# Solo pronósticos
python -m scripts.main --skip-historical

# Ver todas las opciones
python -m scripts.main --help

📊 Datos Generados

El pipeline genera archivos JSON en data/raw/:
historical_<location>_<date>.json - Datos históricos (2020-2025)
forecast_<location>_<date>.json - Pronósticos (7 días)
combined_<location>_<date>.json - Datos combinados


🧪 Testing
# Ejecutar todos los tests
python -m pytest test/ -v

# Ejecutar tests específicos
python -m pytest test/test_config.py -v

🐳 Comandos Docker Útiles

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

📚 Dataset
Para información detallada sobre el dataset y preguntas de negocio, ver DATASET_DESCRIPTION.md.

🛠️ Tecnologías Utilizadas

Python 3.7+ - Lenguaje principal
OpenMeteo API - Fuente de datos meteorológicos
PostgreSQL 12.7 - Base de datos relacional
Docker & Docker Compose - Contenedorización
pandas - Procesamiento de datos
pytest - Testing
requests-cache - Caching de API calls


🔧 Troubleshooting
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