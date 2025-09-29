"""
Cliente de API para OpenMeteo

Maneja las llamadas a las APIs de OpenMeteo para obtener datos históricos
y de pronóstico meteorológico.
"""

import logging
from typing import Optional, Dict, Any
import pandas as pd
import openmeteo_requests
import requests_cache
from retry_requests import retry

from .config import WeatherConfig, Location

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherAPIClient:
    """
    Cliente para interactuar con las APIs de OpenMeteo.
    
    Maneja tanto datos históricos como pronósticos con configuración
    centralizada y manejo robusto de errores.
    """
    
    def __init__(self, config: WeatherConfig = None):
        """
        Inicializa el cliente de API.
        
        Args:
            config: Configuración a usar. Si no se proporciona, usa la por defecto.
        """
        self.config = config or WeatherConfig()
        self._setup_session()
    
    def _setup_session(self) -> None:
        """Configura la sesión con cache y reintentos."""
        logger.info("⚙️ Configurando sesión con cache y reintentos")
        
        cache_session = requests_cache.CachedSession(
            '.cache', 
            expire_after=3600
        )
        retry_session = retry(
            cache_session, 
            retries=self.config.MAX_RETRIES, 
            backoff_factor=0.3
        )
        self.openmeteo = openmeteo_requests.Client(session=retry_session)
    
    def fetch_historical_data(self, location: Location) -> pd.DataFrame:
        """
        Obtiene datos históricos para una ubicación.
        
        Args:
            location: Objeto Location con coordenadas y nombre
            
        Returns:
            pd.DataFrame: Datos meteorológicos históricos
        """
        logger.info(f"📈 Obteniendo datos históricos para {location.name}")
        
        params = {
            "latitude": location.lat,
            "longitude": location.lon,
            "start_date": self.config.HISTORICAL_START_DATE,
            "end_date": self.config.HISTORICAL_END_DATE,
            "daily": self.config.DAILY_VARIABLES,
            "timezone": self.config.TIMEZONE,
        }
        
        return self._fetch_data(
            url=self.config.ARCHIVE_URL,
            params=params,
            location=location,
            data_type="históricos"
        )
    
    def fetch_forecast_data(self, location: Location, 
                          past_days: int = 1, 
                          forecast_days: int = 7) -> pd.DataFrame:
        """
        Obtiene datos de pronóstico para una ubicación.
        
        Args:
            location: Objeto Location con coordenadas y nombre
            past_days: Días hacia atrás a incluir
            forecast_days: Días de pronóstico hacia adelante
            
        Returns:
            pd.DataFrame: Datos meteorológicos de pronóstico
        """
        logger.info(f"🔮 Obteniendo pronóstico para {location.name}")
        
        params = {
            "latitude": location.lat,
            "longitude": location.lon,
            "daily": self.config.DAILY_VARIABLES,
            "timezone": self.config.TIMEZONE,
            "past_days": past_days,
            "forecast_days": forecast_days,
        }
        
        return self._fetch_data(
            url=self.config.FORECAST_URL,
            params=params,
            location=location,
            data_type="pronóstico"
        )
    
    def _fetch_data(self, url: str, params: Dict[str, Any], 
                   location: Location, data_type: str) -> pd.DataFrame:
        """
        Función genérica para obtener datos de cualquier endpoint.
        
        Args:
            url: URL del endpoint
            params: Parámetros de la consulta
            location: Ubicación para la cual obtener datos
            data_type: Tipo de datos (para logging)
            
        Returns:
            pd.DataFrame: Datos meteorológicos
        """
        try:
            # Validar parámetros
            self._validate_params(params)
            
            # Hacer request
            logger.info(f"🌐 Consultando API para datos {data_type}")
            responses = self.openmeteo.weather_api(url, params=params)
            
            if not responses:
                raise ValueError("La API no devolvió datos")
            
            response = responses[0]
            logger.info("✅ Respuesta recibida correctamente")
            
            # Procesar datos
            return self._process_response(response, location)
            
        except requests_cache.requests.exceptions.RequestException as e:
            logger.error(f"❌ Error de conexión: {e}")
            return pd.DataFrame()
            
        except ValueError as e:
            logger.error(f"❌ Error de validación: {e}")
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"❌ Error inesperado para {location.name}: {e}")
            return pd.DataFrame()
    
    def _validate_params(self, params: Dict[str, Any]) -> None:
        """
        Valida los parámetros de la consulta.
        
        Args:
            params: Parámetros a validar
            
        Raises:
            ValueError: Si los parámetros son inválidos
        """
        required_params = ['latitude', 'longitude', 'daily', 'timezone']
        
        for param in required_params:
            if param not in params:
                raise ValueError(f"Parámetro requerido faltante: {param}")
        
        # Validar coordenadas
        if not -90 <= params['latitude'] <= 90:
            raise ValueError(f"Latitud inválida: {params['latitude']}")
        
        if not -180 <= params['longitude'] <= 180:
            raise ValueError(f"Longitud inválida: {params['longitude']}")
    
    def _process_response(self, response, location: Location) -> pd.DataFrame:
        """
        Procesa la respuesta de la API y la convierte a DataFrame.
        
        Args:
            response: Respuesta de la API de OpenMeteo
            location: Ubicación correspondiente a los datos
            
        Returns:
            pd.DataFrame: Datos procesados
        """
        logger.info("📊 Procesando respuesta de la API")
        
        daily = response.Daily()
        
        # Crear índice de fechas
        dates = pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        )
        
        # Construir diccionario de datos
        daily_data = {"date": dates}
        
        for i, var in enumerate(self.config.DAILY_VARIABLES):
            daily_data[var] = daily.Variables(i).ValuesAsNumpy()
        
        # Crear DataFrame
        df = pd.DataFrame(daily_data)
        df["location"] = location.name
        
        logger.info(f"✅ Procesados {len(df)} registros para {location.name}")
        
        return df
    
    def fetch_all_locations_historical(self) -> Dict[str, pd.DataFrame]:
        """
        Obtiene datos históricos para todas las ubicaciones configuradas.
        
        Returns:
            Dict[str, pd.DataFrame]: Diccionario con datos por ubicación
        """
        logger.info("🌍 Obteniendo datos históricos para todas las ubicaciones")
        
        results = {}
        
        for location in self.config.LOCATIONS:
            df = self.fetch_historical_data(location)
            if not df.empty:
                results[location.name] = df
            else:
                logger.warning(f"⚠️ No se obtuvieron datos para {location.name}")
        
        logger.info(f"✅ Completado: {len(results)} ubicaciones procesadas")
        return results
    
    def fetch_all_locations_forecast(self) -> Dict[str, pd.DataFrame]:
        """
        Obtiene datos de pronóstico para todas las ubicaciones configuradas.
        
        Returns:
            Dict[str, pd.DataFrame]: Diccionario con datos por ubicación
        """
        logger.info("🌍 Obteniendo pronósticos para todas las ubicaciones")
        
        results = {}
        
        for location in self.config.LOCATIONS:
            df = self.fetch_forecast_data(location)
            if not df.empty:
                results[location.name] = df
            else:
                logger.warning(f"⚠️ No se obtuvo pronóstico para {location.name}")
        
        logger.info(f"✅ Completado: {len(results)} pronósticos procesados")
        return results

# Función de conveniencia para compatibilidad con código existente
def fetch_weather_data(location_name: str, latitude: float, longitude: float) -> pd.DataFrame:
    """
    Función de compatibilidad para obtener datos históricos.
    
    DEPRECATED: Usar WeatherAPIClient.fetch_historical_data() directamente.
    """
    logger.warning("⚠️ Usando función deprecated. Considera migrar a WeatherAPIClient")
    
    client = WeatherAPIClient()
    location = Location(name=location_name, lat=latitude, lon=longitude)
    return client.fetch_historical_data(location)