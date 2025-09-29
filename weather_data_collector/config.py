"""
Configuración para el Weather Data Collector - OpenMeteo API

Define configuraciones para datos históricos (fijos) y actuales/forecast (dinámicos).
"""

from datetime import date, timedelta
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class Location:
    """Representa una ubicación geográfica con nombre y coordenadas."""
    name: str
    lat: float
    lon: float
    
    def __post_init__(self):
        """Valida que las coordenadas estén en rangos válidos."""
        if not -90 <= self.lat <= 90:
            raise ValueError(f"Latitud inválida: {self.lat}. Debe estar entre -90 y 90.")
        if not -180 <= self.lon <= 180:
            raise ValueError(f"Longitud inválida: {self.lon}. Debe estar entre -180 y 180.")

class WeatherConfig:
    """
    Configuración centralizada para la recolección de datos meteorológicos.
    """
    
    # CONFIGURACIÓN PARA DATOS HISTÓRICOS (FIJOS)
    # La API histórica de OpenMeteo permite datos hasta 2 días antes de hoy
    HISTORICAL_START_DATE = "2020-01-01"
    HISTORICAL_END_DATE = "2025-09-27"  
    
    # CONFIGURACIÓN PARA DATOS ACTUALES/FORECAST (DINÁMICOS)
    @staticmethod
    def get_current_data_date() -> str:
        """
        Calcula la fecha más reciente disponible para datos actuales.
        OpenMeteo histórico: hasta 2 días antes de hoy.
        
        Returns:
            str: Fecha en formato YYYY-MM-DD
        """
        two_days_ago = date.today() - timedelta(days=2)
        return two_days_ago.strftime("%Y-%m-%d")
    
    @staticmethod
    def get_forecast_dates() -> tuple[str, str]:
        """
        Calcula el rango para datos de forecast (próximos 7 días).
        
        Returns:
            tuple: (fecha_inicio, fecha_fin) para forecast
        """
        today = date.today()
        seven_days_ahead = today + timedelta(days=7)
        return today.strftime("%Y-%m-%d"), seven_days_ahead.strftime("%Y-%m-%d")
    
    # Ubicaciones del Corn Belt
    LOCATIONS = [
        Location(name="iowa_center", lat=41.6005, lon=-93.6091),
        Location(name="illinois_center", lat=40.6331, lon=-89.3985)
    ]
    
    # Variables meteorológicas diarias
    DAILY_VARIABLES = [
        "weather_code",                    # Código de clima
        "temperature_2m_max",              # Temperatura máxima a 2m
        "temperature_2m_min",              # Temperatura mínima a 2m  
        "daylight_duration",               # Duración de luz solar
        "precipitation_sum",               # Precipitación total
        "shortwave_radiation_sum",         # Radiación de onda corta
        "et0_fao_evapotranspiration",     # Evapotranspiración FAO
        "soil_moisture_0_to_100cm_mean",  # Humedad del suelo 0-100cm
        "vapour_pressure_deficit_max",    # Déficit de presión de vapor máximo
    ]
    
    # URLs de las APIs de OpenMeteo
    TIMEZONE = "auto"
    ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"      # Datos históricos
    FORECAST_URL = "https://api.open-meteo.com/v1/forecast"            # Datos actuales/forecast
    
    # Configuración de archivos
    OUTPUT_DIR = "data/raw"
    
    # Configuración de requests
    REQUEST_TIMEOUT = 30
    MAX_RETRIES = 3
    RETRY_DELAY = 1
    
    @classmethod
    def get_location_by_name(cls, name: str) -> Location:
        """Busca una ubicación por nombre."""
        for location in cls.LOCATIONS:
            if location.name == name:
                return location
        raise ValueError(f"Ubicación '{name}' no encontrada")
    
    @classmethod
    def validate_config(cls) -> bool:
        """Valida la configuración."""
        # Validar fechas históricas
        start = date.fromisoformat(cls.HISTORICAL_START_DATE)
        end = date.fromisoformat(cls.HISTORICAL_END_DATE)
        
        if start >= end:
            raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")
        
        if not cls.LOCATIONS:
            raise ValueError("Debe haber al menos una ubicación configurada")
            
        if not cls.DAILY_VARIABLES:
            raise ValueError("Debe haber al menos una variable meteorológica configurada")
            
        return True

# Instancia de configuración
config = WeatherConfig()