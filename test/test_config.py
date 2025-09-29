"""
Tests unitarios para el módulo de configuración.

Valida que todas las configuraciones sean correctas y que las
validaciones funcionen apropiadamente.
"""

import pytest
from datetime import date
from weather_data_collector.config import WeatherConfig, Location

class TestLocation:
    """Tests para la clase Location"""
    
    def test_valid_location_creation(self):
        """Test que una ubicación válida se crea correctamente"""
        location = Location("iowa_test", 41.6005, -93.6091)
        
        assert location.name == "iowa_test"
        assert location.lat == 41.6005
        assert location.lon == -93.6091
    
    def test_invalid_latitude_too_high(self):
        """Test que latitud > 90 genera error"""
        with pytest.raises(ValueError, match="Latitud inválida"):
            Location("invalid", 91.0, -93.6091)
    
    def test_invalid_latitude_too_low(self):
        """Test que latitud < -90 genera error"""
        with pytest.raises(ValueError, match="Latitud inválida"):
            Location("invalid", -91.0, -93.6091)
    
    def test_invalid_longitude_too_high(self):
        """Test que longitud > 180 genera error"""
        with pytest.raises(ValueError, match="Longitud inválida"):
            Location("invalid", 41.6005, 181.0)
    
    def test_invalid_longitude_too_low(self):
        """Test que longitud < -180 genera error"""
        with pytest.raises(ValueError, match="Longitud inválida"):
            Location("invalid", 41.6005, -181.0)

class TestWeatherConfig:
    """Tests para la clase WeatherConfig"""
    
    def test_config_initialization(self):
        """Test que la configuración se inicializa correctamente"""
        config = WeatherConfig()
        
        # Verificar que hay ubicaciones
        assert len(config.LOCATIONS) > 0
        
        # Verificar que hay variables meteorológicas
        assert len(config.DAILY_VARIABLES) > 0
        
        # Verificar URLs
        assert "open-meteo.com" in config.ARCHIVE_URL
        assert "open-meteo.com" in config.FORECAST_URL
    
    def test_historical_dates_valid(self):
        """Test que las fechas históricas son válidas"""
        config = WeatherConfig()
        
        start_date = date.fromisoformat(config.HISTORICAL_START_DATE)
        end_date = date.fromisoformat(config.HISTORICAL_END_DATE)
        
        # La fecha de inicio debe ser anterior a la de fin
        assert start_date < end_date
        
        # La fecha de inicio debe ser razonable (después de 2000)
        assert start_date >= date(2000, 1, 1)
        
        # La fecha de fin debe ser anterior a hoy
        assert end_date <= date.today()
    
    def test_get_location_by_name_success(self):
        """Test buscar ubicación por nombre exitoso"""
        config = WeatherConfig()
        
        # Usar la primera ubicación configurada
        first_location = config.LOCATIONS[0]
        found_location = config.get_location_by_name(first_location.name)
        
        assert found_location.name == first_location.name
        assert found_location.lat == first_location.lat
        assert found_location.lon == first_location.lon
    
    def test_get_location_by_name_not_found(self):
        """Test buscar ubicación inexistente genera error"""
        config = WeatherConfig()
        
        with pytest.raises(ValueError, match="no encontrada"):
            config.get_location_by_name("ubicacion_inexistente")
    
    def test_validate_config_success(self):
        """Test que la validación de configuración pasa"""
        config = WeatherConfig()
        
        # La validación debe ser exitosa
        assert config.validate_config() == True
    
    def test_daily_variables_not_empty(self):
        """Test que hay variables meteorológicas configuradas"""
        config = WeatherConfig()
        
        assert len(config.DAILY_VARIABLES) > 0
        assert "temperature_2m_max" in config.DAILY_VARIABLES
        assert "precipitation_sum" in config.DAILY_VARIABLES
    
    def test_locations_have_valid_coordinates(self):
        """Test que todas las ubicaciones tienen coordenadas válidas"""
        config = WeatherConfig()
        
        for location in config.LOCATIONS:
            # Verificar que son instancias de Location (validación automática)
            assert isinstance(location, Location)
            assert -90 <= location.lat <= 90
            assert -180 <= location.lon <= 180
            assert len(location.name) > 0

if __name__ == "__main__":
    # Permitir ejecutar tests directamente
    pytest.main([__file__])