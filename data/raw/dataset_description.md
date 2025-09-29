# Weather Data Collection Project 

## Descripción del Dataset

# 1. Fuente de Datos

Este proyecto utiliza datos meteorológicos obtenidos desde la OpenMeteo API (https://open-meteo.com/), una fuente abierta y gratuita de datos meteorológicos históricos y de pronóstico de alta calidad.


# 2. Características del Dataset

##  2.1 Período temporal:

## 2.1.1 Datos históricos: 2020-01-01 hasta 2025-09-27 (aproximadamente 5.5 años)
## 2.1.2 Datos de pronóstico: 7 días futuros desde la fecha actual

## 2.2 Ubicaciones geográficas:

## 2.2.1 Iowa Center: Latitud 41.6005, Longitud -93.6091
## 2.2.2 Illinois Center: Latitud 40.6331, Longitud -89.3985

Estas ubicaciones fueron seleccionadas por estar en el corazón del Corn Belt estadounidense, una región de gran importancia agrícola.

# 3.  Variables meteorológicas recolectadas:

## 3.1 weather_code - Código de condiciones meteorológicas
## 3.2 temperature_2m_max - Temperatura máxima diaria a 2 metros (°C)
## 3.3 temperature_2m_min - Temperatura mínima diaria a 2 metros (°C)
## 3.4 daylight_duration - Duración de luz solar (segundos)
## 3.5 precipitation_sum - Precipitación total diaria (mm)
## 3.6 shortwave_radiation_sum - Radiación solar de onda corta (MJ/m²)
## 3.7 et0_fao_evapotranspiration - Evapotranspiración de referencia FAO (mm)
## 3.8 soil_moisture_0_to_100cm_mean - Humedad del suelo promedio 0-100cm (m³/m³)
## 3.9 vapour_pressure_deficit_max - Déficit de presión de vapor máximo (kPa)

# 4. Metodología de Recolección
Los datos se obtienen mediante un pipeline automatizado desarrollado en Python que:

- Consulta la API de OpenMeteo para datos históricos y de pronóstico
- Valida la calidad de los datos obtenidos
- Almacena los datos en formato JSON estructurado
- Genera logs detallados del proceso de recolección

# 5. Volumen de datos:

Aproximadamente 2,005 registros por ubicación para datos históricos
8 registros por ubicación para pronósticos (ayer + 7 días futuros)
Total estimado: ~4,000+ registros de datos meteorológicos

# 6. Preguntas de Negocio

## 6.1 Análisis de Tendencias Climáticas
¿Cómo han evolucionado las temperaturas y precipitaciones en el Corn Belt entre 2020-2025 y qué tendencias se pueden identificar?

Esta pregunta permitirá:

Identificar patrones de cambio climático regional
Analizar variaciones estacionales y anuales
Detectar eventos meteorológicos extremos
Evaluar la estabilidad climática para la agricultura

## 6.2. Optimización de Recursos Hídricos
¿Cuál es la relación entre evapotranspiración, humedad del suelo y precipitaciones, y cómo se puede optimizar el uso del agua en agricultura?
Esta pregunta ayudará a:

Identificar períodos de estrés hídrico en cultivos
Optimizar sistemas de irrigación
Predecir necesidades de agua por temporada
Desarrollar estrategias de conservación del agua

## 6.3. Análisis de Radiación Solar y Productividad
¿Existe una correlación entre la radiación solar, duración de luz diurna y las condiciones meteorológicas que afectan el crecimiento de cultivos?
Esta pregunta permitirá:

Evaluar el potencial fotosintético por período
Identificar ventanas óptimas para diferentes cultivos
Analizar el impacto de condiciones nubosas en la productividad
Optimizar calendarios de siembra y cosecha

## 6.4. Comparación Regional y Estrategias Diferenciadas
¿Qué diferencias significativas existen en los patrones meteorológicos entre Iowa e Illinois, y cómo justifican estrategias agrícolas diferenciadas?

Esta pregunta ayudará a:

Identificar ventajas comparativas regionales
Desarrollar estrategias de cultivo específicas por región
Evaluar riesgos meteorológicos diferenciados
Optimizar la diversificación geográfica de cultivos

# Valor del Dataset para Análisis SQL
### Este dataset está estructurado para facilitar consultas SQL complejas que pueden incluir:

### Análisis de series temporales con funciones de ventana
### Agregaciones por períodos (mensual, estacional, anual)
### Comparaciones entre ubicaciones usando JOINs
### Cálculos de correlaciones entre variables meteorológicas
### Identificación de outliers y eventos extremos
### Análisis de tendencias usando regresiones lineales
### La naturaleza normalizada de los datos meteorológicos los hace ideales para análisis estadísticos profundos y modelado predictivo mediante consultas SQL avanzadas.