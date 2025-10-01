# Weather Data Engineering Project

# 📋 Descripción del Proyecto

Pipeline completo de ingeniería de datos que recolecta, almacena y analiza datos meteorológicos de dos ubicaciones en Estados Unidos (Iowa e Illinois) utilizando tecnologías cloud-native y contenedores Docker.

### Tecnologías Utilizadas

- Python 3.11: Scripts de recolección, carga y análisis
- PostgreSQL 12.7: Base de datos relacional
- Docker & Docker Compose: Orquestación de contenedores
- OpenMeteo API: Fuente de datos meteorológicos

# 🎯 Estructura del Proyecto

cloud-data-engineering/
├── data/
│   └── raw/                          # Archivos JSON con datos meteorológicos
├── database/
│   ├── sql/
│   │   └── 01_create_tables.sql      # DDL: Creación de tablas
│   ├── loader/                       # Carga de datos
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── load_data.py
│   └── reporter/                     # Reportes SQL
│       ├── Dockerfile
│       ├── requirements.txt
│       └── generate_report.py
├── weather_data_collector/           # Pipeline de recolección
│   ├── scripts/
│   │   └── main.py
│   └── test/
├── docker-compose.yml                # PostgreSQL en Docker
├── setup_project.ps1                 # Script de setup automatizado
└── README.md

# 🚀 Setup Rápido

 ### Prerrequisitos

  - Docker Desktop instalado y corriendo
  - PowerShell (Windows) o Bash (Linux/Mac)
  - Git

### Instalación Automática
   
    git clone https://github.com/nsaldarriaga/cloud-data-engineering-.git
    cd cloud-data-engineering-

    .\setup_project.ps1 ### script de setup automático

Este script ejecutará automáticamente:

- Levantar PostgreSQL con Docker Compose
- Crear las tablas en la base de datos
- Construir la imagen del data loader
- Cargar los datos desde archivos JSON
- Construir la imagen del reporter
- Verificar que los datos se cargaron correctamente

Tiempo estimado: 3-5 minutos 

# 📚 Setup Manual 

Si prefieres ejecutar cada paso manualmente o el script automatizado no funciona en tu sistema:

- Paso 1: Levantar PostgreSQL (Ejercicio 2)
  docker-compose up -d 

- Paso 2: verificar 
  docker ps 

- Paso 3:  Crear las Tablas (Ejercicio 3)
  Get-Content .\database\sql\01_create_tables.sql | docker exec -i weather_postgres psql -U weather_user -d weather_db 

- Paso 4: Construir la imagen del loader (Ejercicio 4)
  cd database/loader
  docker build -t weather-data-loader .
  cd ../.. 

- Paso 5: Ejecutar la carga de datos (Ejercicio 4)
  docker run --rm --network host -v ${PWD}/data:/data weather-data-loader 

- Paso 6: Construir el Reporter (Ejercicio 5)
  cd database/reporter
  docker build -t weather-reporter .
  cd ../..

- Paso 7: Ver reporte
  docker run --rm --network host weather-reporter

# Consultas Incluidas

 El reporte incluye 5 consultas que agregan valor al negocio:

1. Promedio de temperaturas por ubicación - Identificar diferencias climáticas regionales
2. Días con precipitación - Evaluar riesgo de inundaciones y necesidades de drenaje
3. Temperaturas extremas registradas - Identificar riesgos climáticos extremos
4. Precipitación mensual 2024 - Patrones estacionales para planificación agrícola
5. Comparación histórico vs pronóstico - Evaluar tendencias futuras

# 🔍 Consultas Manuales a la Base de Datos

- Conectarse a PostgreSQL
  docker exec -it weather_postgres psql -U weather_user -d weather_db

- Ver las tablas
  \dt

- Ver estructura de una tabla
  \d weather_data

- Contar registros totales
  SELECT COUNT(*) FROM weather_data;

- Registros por tipo (históricos vs pronósticos)
  SELECT data_type, COUNT(*) 
  FROM weather_data 
  GROUP BY data_type;

- Últimas temperaturas registradas
  SELECT l.location_name, w.date, w.temperature_2m_max
  FROM weather_data w
  LEFT JOIN locations l ON w.location_id = l.id
  ORDER BY w.date DESC
  LIMIT 10;

- Salir
  \q

# 🗄️ Base de datos (DDL)

- Tablas:
  
 1. locations
  - id (INTEGER, PK)
  - location_name (VARCHAR)
  - created_at (TIMESTAMP)

 2. weather_data
  - id (SERIAL, PK)
  - location_id (INTEGER, FK → locations)
  - date (TIMESTAMP)
  - data_type (VARCHAR): 'historical' o 'forecast'
  - Variables meteorológicas (REAL)
  - created_at (TIMESTAMP)

 3. Constraints:
  - Foreign Key: fk_weather_location
  - Unique: unique_location_date_type

 4. Índices:
  - idx_weather_date
  - idx_weather_location_type
  - idx_weather_location_date

# 🧪 Verificación y Testing
 
  ### 1. PostgreSQL corriendo
    docker ps | Select-String "weather_postgres"

  ### 2. Datos cargados
    docker exec weather_postgres psql -U weather_user -d weather_db -c "SELECT COUNT(*) FROM weather_data;"

  ### 3. Imágenes construidas
    docker images | Select-String "weather"

  ### 4. Generar reporte de prueba
    docker run --rm --network host weather-reporter

# 📈 Datos del Proyecto

- Ubicaciones monitoreadas: 2 (Iowa Center, Illinois Center)
- Periodo histórico: 2020-01-01 a 2025-09-27 (~2,097 días)
- Pronósticos: 7-8 días futuros
- Total registros: ~4,210
- Variables meteorológicas: 10 por registro
- Frecuencia: Datos diarios


# 🔗 Enlaces Útiles

- OpenMeteo API: https://open-meteo.com/
- Docker Documentation: https://docs.docker.com/_/postgres
- PostgreSQL Documentation: https://www.postgresql.org/docs/