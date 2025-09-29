# TP Final - Fundación de Cloud Data Engeneering - ITBA

Weather Data Collection Pipeline
ITBA - Cloud Data Engineering - Trabajo Práctico Final
Pipeline automatizado para recolección y procesamiento de datos meteorológicos desde OpenMeteo API.

Estructura del Proyecto

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
├── DATASET_DESCRIPTION.md     # Descripción del dataset y preguntas de negocio
├── requirements.txt
├── .gitignore
└── README.md

Instalación

# Clonar repositorio
git clone <https://github.com/nsaldarriaga/cloud-data-engineering-.git>
cd <cloud-data-engineering->

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación ejecutando tests
python -m pytest test/ -v

Uso
Ejecutar pipeline completo
python -m scripts.main

Ejecutar solo datos históricos
python -m scripts.main --skip-forecast

Ejecutar solo pronósticos
python -m scripts.main --skip-historical

Opciones adicionales
python -m scripts.main --help

Datos Generados
El pipeline genera archivos JSON en data/raw/:

historical_<location>_<date>.json - Datos históricos (2020-2025)
forecast_<location>_<date>.json - Pronósticos (7 días)
combined_<location>_<date>.json - Datos combinados

Testing
# Ejecutar todos los tests
python -m pytest test/ -v

# Ejecutar tests específicos
python -m pytest test/test_config.py -v

Dataset
Para información detallada sobre el dataset y preguntas de negocio, ver DATASET_DESCRIPTION.md.

Tecnologías Utilizadas
Python 3.7+
OpenMeteo API - Fuente de datos meteorológicos
pandas - Procesamiento de datos
pytest - Testing
requests-cache - Caching de API calls

Estado del Proyecto

✅ Ejercicio 1: Elección de dataset y preguntas de negocio
🔄 Ejercicio 2: En desarrollo
⏳ Ejercicio 3: Pendiente
⏳ Ejercicio 4: Pendiente
⏳ Ejercicio 5: Pendiente
⏳ Ejercicio 6: Pendiente