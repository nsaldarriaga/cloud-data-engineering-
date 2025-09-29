"""
Weather Data Collector

Un módulo para recolectar datos meteorológicos desde APIs externas
y prepararlos para almacenamiento en bases de datos.
"""

__version__ = "0.1.0"
__author__ = "Neptali Saldarriaga"
__description__ = "Collector de datos meteorológicos desde API Open Meteo"

# Importar las clases/funciones principales que queremos exponer
from .api_client import WeatherAPIClient
from .config import WeatherConfig

# Definir qué se exporta cuando alguien hace "from weather_data_collector import *"
__all__ = [
    "WeatherAPIClient",
    "WeatherConfig",
    "__version__"
]