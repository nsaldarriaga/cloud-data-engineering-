"""
Weather Data Loader - Ejercicio 4
Carga datos históricos y pronósticos desde archivos JSON a PostgreSQL
"""

import json
import psycopg2
from psycopg2.extras import execute_batch
import os
import sys
from datetime import datetime

# Configuración de conexión a PostgreSQL
DB_CONFIG = {
    'host': 'localhost',  # Desde container Docker a localhost del host
    'port': 5432,
    'database': 'weather_db',
    'user': 'weather_user',
    'password': 'weather_pass'
}

# Ruta donde estarán montados los archivos JSON (volumen -v)
DATA_PATH = '/data/raw'

# Mapeo de nombres de ubicaciones a IDs
LOCATIONS = {
    'iowa_center': 1,
    'illinois_center': 2
}


def log(message):
    """Función helper para logging con timestamp"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] {message}")


def connect_db():
    """Establece conexión con PostgreSQL"""
    log("Conectando a PostgreSQL...")
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        log("✓ Conexión exitosa")
        return conn
    except psycopg2.Error as e:
        log(f"✗ Error de conexión: {e}")
        sys.exit(1)


def insert_locations(conn):
    """Inserta las ubicaciones en la tabla locations"""
    log("Insertando ubicaciones...")
    cursor = conn.cursor()
    
    try:
        for location_name, location_id in LOCATIONS.items():
            cursor.execute("""
                INSERT INTO locations (id, location_name)
                VALUES (%s, %s)
                ON CONFLICT (id) DO NOTHING
            """, (location_id, location_name))
        
        conn.commit()
        log(f"✓ {len(LOCATIONS)} ubicaciones insertadas/verificadas")
    except psycopg2.Error as e:
        log(f"✗ Error insertando ubicaciones: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()


def drop_foreign_key(conn):
    """Remueve temporalmente la foreign key constraint"""
    log("Removiendo constraint fk_weather_location...")
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            ALTER TABLE weather_data 
            DROP CONSTRAINT IF EXISTS fk_weather_location
        """)
        conn.commit()
        log("✓ Constraint removida temporalmente")
    except psycopg2.Error as e:
        log(f"✗ Error removiendo constraint: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()


def recreate_foreign_key(conn):
    """Recrea la foreign key constraint"""
    log("Recreando constraint fk_weather_location...")
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            ALTER TABLE weather_data 
            ADD CONSTRAINT fk_weather_location 
            FOREIGN KEY (location_id) 
            REFERENCES locations(id)
        """)
        conn.commit()
        log("✓ Constraint recreada exitosamente")
    except psycopg2.Error as e:
        log(f"✗ Error recreando constraint: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()


def load_json_file(filepath):
    """Lee un archivo JSONL y retorna lista de registros"""
    records = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():  # Ignorar líneas vacías
                    records.append(json.loads(line))
        return records
    except FileNotFoundError:
        log(f"✗ Archivo no encontrado: {filepath}")
        return []
    except json.JSONDecodeError as e:
        log(f"✗ Error parseando JSON en {filepath}: {e}")
        return []


def insert_weather_data(conn, records, data_type):
    """
    Inserta registros de clima en la tabla weather_data usando batch insert
    
    Args:
        conn: Conexión a PostgreSQL
        records: Lista de diccionarios con datos de clima
        data_type: 'historical' o 'forecast'
    """
    if not records:
        log(f"⚠ No hay registros para insertar ({data_type})")
        return
    
    cursor = conn.cursor()
    
    # Preparar datos para inserción batch
    insert_data = []
    for record in records:
        location_id = LOCATIONS.get(record['location'])
        if not location_id:
            log(f"⚠ Ubicación desconocida: {record['location']}")
            continue
        
        insert_data.append((
            location_id,
            record['date'],
            data_type,
            record.get('weather_code'),
            record.get('temperature_2m_max'),
            record.get('temperature_2m_min'),
            record.get('daylight_duration'),
            record.get('shortwave_radiation_sum'),
            record.get('precipitation_sum'),
            record.get('et0_fao_evapotranspiration'),
            record.get('soil_moisture_0_to_100cm_mean'),  # Puede ser NULL
            record.get('vapour_pressure_deficit_max')
        ))
    
    # Inserción por lotes (más eficiente)
    try:
        execute_batch(cursor, """
            INSERT INTO weather_data (
                location_id, date, data_type, weather_code,
                temperature_2m_max, temperature_2m_min, daylight_duration,
                shortwave_radiation_sum, precipitation_sum,
                et0_fao_evapotranspiration, soil_moisture_0_to_100cm_mean,
                vapour_pressure_deficit_max
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (location_id, date, data_type) DO NOTHING
        """, insert_data, page_size=500)
        
        conn.commit()
        log(f"✓ {len(insert_data)} registros {data_type} insertados")
    except psycopg2.Error as e:
        log(f"✗ Error insertando datos {data_type}: {e}")
        conn.rollback()
        raise
    finally:
        cursor.close()


def verify_data(conn):
    """Verifica que los datos se hayan cargado correctamente"""
    log("\n=== Verificando datos cargados ===")
    cursor = conn.cursor()
    
    try:
        # Contar ubicaciones
        cursor.execute("SELECT COUNT(*) FROM locations")
        location_count = cursor.fetchone()[0]
        log(f"Ubicaciones: {location_count}")
        
        # Contar registros históricos
        cursor.execute("SELECT COUNT(*) FROM weather_data WHERE data_type = 'historical'")
        historical_count = cursor.fetchone()[0]
        log(f"Datos históricos: {historical_count}")
        
        # Contar pronósticos
        cursor.execute("SELECT COUNT(*) FROM weather_data WHERE data_type = 'forecast'")
        forecast_count = cursor.fetchone()[0]
        log(f"Pronósticos: {forecast_count}")
        
        # Total
        cursor.execute("SELECT COUNT(*) FROM weather_data")
        total_count = cursor.fetchone()[0]
        log(f"Total registros: {total_count}")
        
        # Rangos de fechas por ubicación
        cursor.execute("""
            SELECT l.location_name, 
                   MIN(w.date)::date as fecha_min, 
                   MAX(w.date)::date as fecha_max,
                   COUNT(*) as registros
            FROM weather_data w
            JOIN locations l ON w.location_id = l.id
            GROUP BY l.location_name
            ORDER BY l.location_name
        """)
        
        log("\nResumen por ubicación:")
        for row in cursor.fetchall():
            log(f"  {row[0]}: {row[3]} registros ({row[1]} a {row[2]})")
        
    except psycopg2.Error as e:
        log(f"✗ Error verificando datos: {e}")
    finally:
        cursor.close()


def main():
    """Función principal del loader"""
    log("=== Iniciando carga de datos meteorológicos ===\n")
    
    # 1. Conectar a la base de datos
    conn = connect_db()
    
    try:
        # 2. Insertar ubicaciones
        insert_locations(conn)
        
        # 3. Remover constraint temporalmente
        drop_foreign_key(conn)
        
        # 4. Cargar datos históricos
        log("\n--- Cargando datos históricos ---")
        for location in ['iowa_center', 'illinois_center']:
            filename = f"historical_{location}_2025-09-27.json"
            filepath = os.path.join(DATA_PATH, filename)
            log(f"Leyendo {filename}...")
            records = load_json_file(filepath)
            log(f"  {len(records)} registros encontrados")
            insert_weather_data(conn, records, 'historical')
        
        # 5. Cargar pronósticos
        log("\n--- Cargando pronósticos ---")
        for location in ['iowa_center', 'illinois_center']:
            filename = f"forecast_{location}_20250929.json"
            filepath = os.path.join(DATA_PATH, filename)
            log(f"Leyendo {filename}...")
            records = load_json_file(filepath)
            log(f"  {len(records)} registros encontrados")
            insert_weather_data(conn, records, 'forecast')
        
        # 6. Recrear constraint
        log("")
        recreate_foreign_key(conn)
        
        # 7. Verificar datos
        verify_data(conn)
        
        log("\n=== ✓ Carga completada exitosamente ===")
        
    except Exception as e:
        log(f"\n✗ Error durante la carga: {e}")
        sys.exit(1)
    finally:
        conn.close()
        log("Conexión cerrada")


if __name__ == "__main__":
    main()