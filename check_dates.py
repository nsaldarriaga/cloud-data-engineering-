import pandas as pd
from pathlib import Path
import json

def check_file_dates(filepath):
    """Verifica fechas mínima y máxima de un archivo JSON"""
    print(f"\n📁 Archivo: {filepath.name}")
    
    try:
        # Leer archivo JSON Lines
        df = pd.read_json(filepath, lines=True)
        
        if df.empty:
            print("   ❌ Archivo vacío")
            return
        
        # Convertir fechas
        df['date'] = pd.to_datetime(df['date'])
        
        # Estadísticas
        print(f"   📊 Total registros: {len(df)}")
        print(f"   📅 Fecha mínima: {df['date'].min().strftime('%Y-%m-%d')}")
        print(f"   📅 Fecha máxima: {df['date'].max().strftime('%Y-%m-%d')}")
        print(f"   🌍 Ubicación: {df['location'].iloc[0]}")
        
        # Verificar variables meteorológicas
        weather_vars = [col for col in df.columns if col not in ['date', 'location']]
        print(f"   🌡️  Variables: {len(weather_vars)} ({', '.join(weather_vars[:3])}...)")
        
        # Verificar datos nulos
        null_counts = df.isnull().sum()
        if null_counts.sum() > 0:
            print(f"   ⚠️  Datos nulos encontrados:")
            for col, nulls in null_counts[null_counts > 0].items():
                print(f"      {col}: {nulls} nulos")
        else:
            print(f"   ✅ Sin datos nulos")
            
    except Exception as e:
        print(f"   ❌ Error leyendo archivo: {e}")

# Verificar todos los archivos
data_dir = Path("data/raw")
json_files = list(data_dir.glob("*.json"))

print("🔍 VERIFICACIÓN DE DATOS GENERADOS")
print("=" * 50)

for json_file in sorted(json_files):
    check_file_dates(json_file)

print("\n" + "=" * 50)
print("✅ Verificación completada")