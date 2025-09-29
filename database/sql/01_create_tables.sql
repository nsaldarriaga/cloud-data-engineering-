-- =============================================================================
-- Script de Creación de Tablas - Weather Data Pipeline
-- ITBA - Cloud Data Engineering - Ejercicio 3
-- =============================================================================
-- Este script crea la estructura de base de datos para almacenar datos
-- meteorológicos históricos y pronósticos de múltiples ubicaciones.
-- =============================================================================

-- Eliminar tablas si existen (para poder re-ejecutar el script)
DROP TABLE IF EXISTS weather_data CASCADE;
DROP TABLE IF EXISTS locations CASCADE;

-- =============================================================================
-- Tabla: locations
-- Descripción: Almacena información de las ubicaciones meteorológicas
-- =============================================================================
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    location_name VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Índice para búsquedas rápidas por nombre
    CONSTRAINT unique_location_name UNIQUE (location_name)
);

-- Comentarios de documentación
COMMENT ON TABLE locations IS 'Ubicaciones geográficas para datos meteorológicos';
COMMENT ON COLUMN locations.location_name IS 'Nombre único de la ubicación (ej: iowa_center)';

-- =============================================================================
-- Tabla: weather_data
-- Descripción: Almacena todos los datos meteorológicos (históricos y pronósticos)
-- =============================================================================
CREATE TABLE weather_data (
    id SERIAL PRIMARY KEY,
    location_id INTEGER NOT NULL,
    date DATE NOT NULL,
    data_type VARCHAR(20) NOT NULL CHECK (data_type IN ('historical', 'forecast')),
    
    -- Variables meteorológicas principales
    weather_code DECIMAL(5,1),
    temperature_2m_max DECIMAL(6,2),
    temperature_2m_min DECIMAL(6,2),
    
    -- Radiación y luz solar
    daylight_duration DECIMAL(10,2),
    shortwave_radiation_sum DECIMAL(10,4),
    
    -- Precipitación y evapotranspiración
    precipitation_sum DECIMAL(8,2),
    et0_fao_evapotranspiration DECIMAL(10,4),
    
    -- Humedad del suelo y presión de vapor
    soil_moisture_0_to_100cm_mean DECIMAL(10,6),
    vapour_pressure_deficit_max DECIMAL(10,4),
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraint: Cada ubicación solo puede tener un registro por fecha y tipo
    CONSTRAINT unique_location_date_type UNIQUE (location_id, date, data_type)
);

-- Comentarios de documentación
COMMENT ON TABLE weather_data IS 'Datos meteorológicos históricos y pronósticos';
COMMENT ON COLUMN weather_data.data_type IS 'Tipo de dato: historical o forecast';
COMMENT ON COLUMN weather_data.weather_code IS 'Código WMO del clima';
COMMENT ON COLUMN weather_data.temperature_2m_max IS 'Temperatura máxima a 2m (°C)';
COMMENT ON COLUMN weather_data.temperature_2m_min IS 'Temperatura mínima a 2m (°C)';
COMMENT ON COLUMN weather_data.daylight_duration IS 'Duración de luz diurna (segundos)';
COMMENT ON COLUMN weather_data.precipitation_sum IS 'Precipitación total (mm)';
COMMENT ON COLUMN weather_data.et0_fao_evapotranspiration IS 'Evapotranspiración de referencia (mm)';
COMMENT ON COLUMN weather_data.soil_moisture_0_to_100cm_mean IS 'Humedad del suelo promedio 0-100cm (m³/m³)';

-- =============================================================================
-- Foreign Keys (con nombres explícitos para poder removerlas en Ejercicio 4)
-- =============================================================================
ALTER TABLE weather_data 
ADD CONSTRAINT fk_weather_location 
FOREIGN KEY (location_id) REFERENCES locations(id) 
ON DELETE CASCADE;

-- =============================================================================
-- Índices para optimizar consultas comunes
-- =============================================================================
-- Índice para búsquedas por fecha
CREATE INDEX idx_weather_date ON weather_data(date);

-- Índice para búsquedas por ubicación y tipo
CREATE INDEX idx_weather_location_type ON weather_data(location_id, data_type);

-- Índice compuesto para consultas de rango de fechas por ubicación
CREATE INDEX idx_weather_location_date ON weather_data(location_id, date);

-- =============================================================================
-- Verificación de la estructura creada
-- =============================================================================
-- Para verificar que todo se creó correctamente, ejecuta:
-- \dt        -- Lista todas las tablas
-- \d+ locations      -- Describe la tabla locations
-- \d+ weather_data   -- Describe la tabla weather_data