"""
Weather Data Reporter - Ejercicio 5
Genera reportes con consultas SQL que agregan valor al negocio
"""

import psycopg2
from datetime import datetime
import sys

# Configuración de conexión a PostgreSQL
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'weather_db',
    'user': 'weather_user',
    'password': 'weather_pass'
}


def print_header(title):
    """Imprime un encabezado formateado para el reporte"""
    width = 80
    print("\n" + "=" * width)
    print(f"{title.center(width)}")
    print("=" * width + "\n")


def print_separator():
    """Imprime una línea separadora"""
    print("-" * 80)


def connect_db():
    """Establece conexión con PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Error de conexión a la base de datos: {e}")
        sys.exit(1)


def query_1_temperature_averages(cursor):
    """
    Consulta 1: Promedio de temperaturas por ubicación
    Valor de negocio: Identificar diferencias climáticas entre regiones
    """
    print_header("CONSULTA 1: Promedio de Temperaturas por Ubicación")
    
    query = """
        SELECT 
            l.location_name,
            ROUND(AVG(w.temperature_2m_max)::numeric, 2) as temp_max_promedio,
            ROUND(AVG(w.temperature_2m_min)::numeric, 2) as temp_min_promedio,
            ROUND((AVG(w.temperature_2m_max) + AVG(w.temperature_2m_min)) / 2::numeric, 2) as temp_promedio
        FROM weather_data w
        JOIN locations l ON w.location_id = l.id
        WHERE w.data_type = 'historical'
        GROUP BY l.location_name
        ORDER BY l.location_name
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print("📊 Análisis de temperaturas históricas (2020-2025)\n")
    print(f"{'Ubicación':<20} {'Temp. Máx. Prom.':<20} {'Temp. Mín. Prom.':<20} {'Temp. Promedio':<20}")
    print_separator()
    
    for row in results:
        print(f"{row[0]:<20} {row[1]:>17}°C {row[2]:>17}°C {row[3]:>17}°C")
    
    print("\n💡 Insight: Útil para planificar cultivos según rangos térmicos de cada región.\n")


def query_2_rainy_days(cursor):
    """
    Consulta 2: Días con precipitación por ubicación
    Valor de negocio: Evaluar riesgo de inundaciones y necesidades de drenaje
    """
    print_header("CONSULTA 2: Análisis de Días con Precipitación")
    
    query = """
        SELECT 
            l.location_name,
            COUNT(*) as total_dias,
            SUM(CASE WHEN w.precipitation_sum > 0 THEN 1 ELSE 0 END) as dias_con_lluvia,
            ROUND((SUM(CASE WHEN w.precipitation_sum > 0 THEN 1 ELSE 0 END)::numeric / COUNT(*) * 100), 2) as porcentaje_lluvia,
            ROUND(AVG(w.precipitation_sum)::numeric, 2) as precipitacion_promedio
        FROM weather_data w
        JOIN locations l ON w.location_id = l.id
        WHERE w.data_type = 'historical'
        GROUP BY l.location_name
        ORDER BY dias_con_lluvia DESC
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print("🌧️ Frecuencia de precipitaciones (2020-2025)\n")
    print(f"{'Ubicación':<20} {'Total Días':<15} {'Días Lluvia':<15} {'% Lluvia':<15} {'Prom. (mm)':<15}")
    print_separator()
    
    for row in results:
        print(f"{row[0]:<20} {row[1]:<15} {row[2]:<15} {row[3]:>12}% {row[4]:>12}")
    
    print("\n💡 Insight: Mayor frecuencia de lluvia indica necesidad de sistemas de drenaje.\n")


def query_3_extreme_temperatures(cursor):
    """
    Consulta 3: Temperaturas extremas registradas
    Valor de negocio: Identificar riesgos climáticos extremos
    """
    print_header("CONSULTA 3: Temperaturas Extremas Registradas")
    
    query = """
        SELECT 
            l.location_name,
            MAX(w.temperature_2m_max) as temp_max_absoluta,
            (SELECT date::date FROM weather_data w2 
             WHERE w2.location_id = w.location_id 
             AND w2.temperature_2m_max = MAX(w.temperature_2m_max) 
             LIMIT 1) as fecha_max,
            MIN(w.temperature_2m_min) as temp_min_absoluta,
            (SELECT date::date FROM weather_data w3 
             WHERE w3.location_id = w.location_id 
             AND w3.temperature_2m_min = MIN(w.temperature_2m_min) 
             LIMIT 1) as fecha_min
        FROM weather_data w
        JOIN locations l ON w.location_id = l.id
        WHERE w.data_type = 'historical'
        GROUP BY l.location_name, w.location_id
        ORDER BY l.location_name
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print("🌡️ Temperaturas máximas y mínimas absolutas\n")
    print(f"{'Ubicación':<20} {'Máx. Absoluta':<25} {'Mín. Absoluta':<25}")
    print_separator()
    
    for row in results:
        print(f"{row[0]:<20} {row[1]:>8}°C ({row[2]}) {row[3]:>12}°C ({row[4]})")
    
    print("\n💡 Insight: Ayuda a preparar infraestructura para condiciones extremas.\n")


def query_4_monthly_precipitation_2024(cursor):
    """
    Consulta 4: Precipitación promedio mensual en 2024
    Valor de negocio: Patrones estacionales para planificación agrícola
    """
    print_header("CONSULTA 4: Precipitación Mensual Promedio - Año 2024")
    
    query = """
        SELECT 
            l.location_name,
            EXTRACT(MONTH FROM w.date) as mes,
            ROUND(AVG(w.precipitation_sum)::numeric, 2) as precipitacion_promedio,
            COUNT(*) as dias_registrados
        FROM weather_data w
        JOIN locations l ON w.location_id = l.id
        WHERE w.data_type = 'historical'
        AND EXTRACT(YEAR FROM w.date) = 2024
        GROUP BY l.location_name, EXTRACT(MONTH FROM w.date)
        ORDER BY l.location_name, mes
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    meses = {1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
             7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'}
    
    print("📅 Promedio de precipitaciones por mes en 2024\n")
    
    current_location = None
    for row in results:
        if current_location != row[0]:
            if current_location is not None:
                print()
            current_location = row[0]
            print(f"📍 {row[0]}:")
            print(f"  {'Mes':<10} {'Precipitación (mm)':<20} {'Días':<10}")
            print("  " + "-" * 40)
        
        mes_nombre = meses.get(int(row[1]), str(row[1]))
        print(f"  {mes_nombre:<10} {row[2]:>17} {row[3]:>10}")
    
    print("\n💡 Insight: Identificar meses más lluviosos para timing de siembra/cosecha.\n")


def query_5_forecast_comparison(cursor):
    """
    Consulta 5: Comparación entre datos recientes y pronósticos
    Valor de negocio: Evaluar tendencias futuras vs históricas recientes
    """
    print_header("CONSULTA 5: Comparación Datos Recientes vs Pronósticos")
    
    query = """
        SELECT 
            l.location_name,
            w.data_type,
            ROUND(AVG(w.temperature_2m_max)::numeric, 2) as temp_max_promedio,
            ROUND(AVG(w.precipitation_sum)::numeric, 2) as precip_promedio,
            COUNT(*) as registros
        FROM weather_data w
        JOIN locations l ON w.location_id = l.id
        WHERE (w.data_type = 'forecast')
           OR (w.data_type = 'historical' AND w.date >= (SELECT MAX(date) - INTERVAL '30 days' FROM weather_data WHERE data_type = 'historical'))
        GROUP BY l.location_name, w.data_type
        ORDER BY l.location_name, w.data_type DESC
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print("🔮 Comparativa: Últimos 30 días vs Pronóstico\n")
    print(f"{'Ubicación':<20} {'Tipo':<15} {'Temp. Máx. Prom.':<20} {'Precip. Prom.':<20} {'Registros':<12}")
    print_separator()
    
    for row in results:
        tipo_label = "📊 Histórico" if row[1] == 'historical' else "🔮 Pronóstico"
        print(f"{row[0]:<20} {tipo_label:<15} {row[2]:>17}°C {row[3]:>17}mm {row[4]:>12}")
    
    print("\n💡 Insight: Detectar cambios esperados en temperatura y precipitación.\n")


def generate_summary(cursor):
    """Genera un resumen ejecutivo del reporte"""
    print_header("RESUMEN EJECUTIVO")
    
    # Total de registros
    cursor.execute("SELECT COUNT(*) FROM weather_data")
    total_records = cursor.fetchone()[0]
    
    # Rango de fechas
    cursor.execute("""
        SELECT MIN(date)::date, MAX(date)::date 
        FROM weather_data 
        WHERE data_type = 'historical'
    """)
    fecha_min, fecha_max = cursor.fetchone()
    
    print(f"📈 Total de registros en base de datos: {total_records:,}")
    print(f"📅 Rango de datos históricos: {fecha_min} a {fecha_max}")
    print(f"🌍 Ubicaciones monitoreadas: 2 (Iowa Center, Illinois Center)")
    print(f"📊 Tipos de datos: Históricos y Pronósticos")
    print(f"\n⏰ Reporte generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n" + "=" * 80 + "\n")


def main():
    """Función principal que ejecuta todas las consultas"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " REPORTE DE ANÁLISIS METEOROLÓGICO ".center(78) + "║")
    print("║" + " Weather Data Engineering Project ".center(78) + "║")
    print("╚" + "=" * 78 + "╝")
    
    # Conectar a la base de datos
    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        # Ejecutar todas las consultas
        query_1_temperature_averages(cursor)
        query_2_rainy_days(cursor)
        query_3_extreme_temperatures(cursor)
        query_4_monthly_precipitation_2024(cursor)
        query_5_forecast_comparison(cursor)
        
        # Resumen final
        generate_summary(cursor)
        
        print("✅ Reporte generado exitosamente\n")
        
    except Exception as e:
        print(f"\n❌ Error generando reporte: {e}\n")
        sys.exit(1)
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    main()