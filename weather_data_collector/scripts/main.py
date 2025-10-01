"""
Script principal para recolección de datos meteorológicos.

Ejecuta la recolección de datos históricos y/o de pronóstico para
todas las ubicaciones configuradas, con validación y manejo de errores.
"""

import argparse
import logging
from pathlib import Path
from typing import List, Optional
import pandas as pd

# Imports del paquete weather_data_collector
from weather_data_collector.api_client import WeatherAPIClient
from weather_data_collector.config import WeatherConfig, Location
from weather_data_collector.utils import DataUtils

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WeatherDataPipeline:
    """
    Pipeline principal para la recolección de datos meteorológicos.
    
    Coordina la obtención, validación y almacenamiento de datos
    desde las APIs de OpenMeteo.
    """
    
    def __init__(self, config: Optional[WeatherConfig] = None):
        """
        Inicializa el pipeline.
        
        Args:
            config: Configuración a usar. Si no se proporciona, usa la por defecto.
        """
        self.config = config or WeatherConfig()
        self.api_client = WeatherAPIClient(self.config)
        self.data_utils = DataUtils()
        
        # Crear directorio de salida
        Path(self.config.OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
        
        logger.info("🚀 Pipeline inicializado")
    
    def process_location_historical(self, location: Location) -> bool:
        """
        Procesa datos históricos para una ubicación específica.
        
        Args:
            location: Ubicación a procesar
            
        Returns:
            bool: True si se procesó correctamente
        """
        logger.info(f"📈 Procesando datos históricos para {location.name}")
        
        try:
            # Obtener datos
            df = self.api_client.fetch_historical_data(location)
            
            if df.empty:
                logger.warning(f"⚠️ No se obtuvieron datos históricos para {location.name}")
                return False
            
            # Validar calidad de datos
            quality_report = self.data_utils.validate_data_quality(df, location.name)
            if quality_report["status"] == "error":
                logger.error(f"❌ Datos históricos inválidos para {location.name}")
                return False
            
            # Guardar archivo
            filename = f"historical_{location.name}_{self.config.HISTORICAL_END_DATE}.json"
            output_path = Path(self.config.OUTPUT_DIR) / filename
            
            success = self.data_utils.save_to_json(df, output_path)
            
            if success:
                logger.info(f"✅ Datos históricos guardados para {location.name}")
                return True
            else:
                logger.error(f"❌ Error guardando datos históricos para {location.name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error procesando históricos para {location.name}: {e}")
            return False
    
    def process_location_forecast(self, location: Location) -> bool:
        """
        Procesa datos de pronóstico para una ubicación específica.
        
        Args:
            location: Ubicación a procesar
            
        Returns:
            bool: True si se procesó correctamente
        """
        logger.info(f"🔮 Procesando pronóstico para {location.name}")
        
        try:
            # Obtener datos
            df = self.api_client.fetch_forecast_data(location)
            
            if df.empty:
                logger.warning(f"⚠️ No se obtuvo pronóstico para {location.name}")
                return False
            
            # Validar calidad de datos
            quality_report = self.data_utils.validate_data_quality(df, location.name)
            if quality_report["status"] == "error":
                logger.error(f"❌ Datos de pronóstico inválidos para {location.name}")
                return False
            
            # Guardar archivo
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d")
            filename = f"forecast_{location.name}_{timestamp}.json"
            output_path = Path(self.config.OUTPUT_DIR) / filename
            
            success = self.data_utils.save_to_json(df, output_path)
            
            if success:
                logger.info(f"✅ Pronóstico guardado para {location.name}")
                return True
            else:
                logger.error(f"❌ Error guardando pronóstico para {location.name}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error procesando pronóstico para {location.name}: {e}")
            return False
    
    def merge_datasets(self, location: Location, 
                      df_historical: pd.DataFrame, 
                      df_forecast: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        Combina datasets histórico y de pronóstico de forma inteligente.
        
        Args:
            location: Ubicación correspondiente
            df_historical: Datos históricos
            df_forecast: Datos de pronóstico
            
        Returns:
            pd.DataFrame or None: Dataset combinado o None si hay error
        """
        try:
            if df_historical.empty or df_forecast.empty:
                logger.warning(f"⚠️ No se puede combinar datos vacíos para {location.name}")
                return None
            
            logger.info(f"🔄 Combinando datasets para {location.name}")
            
            # Asegurar que las fechas sean datetime
            df_historical['date'] = pd.to_datetime(df_historical['date'])
            df_forecast['date'] = pd.to_datetime(df_forecast['date'])
            
            # Combinar datos
            df_combined = pd.concat([df_historical, df_forecast], ignore_index=True)
            
            # Eliminar duplicados (priorizando datos más recientes - forecast)
            df_combined = df_combined.sort_values(['date', 'location'])
            df_combined = df_combined.drop_duplicates(
                subset=['date', 'location'], 
                keep='last'  # Mantener el más reciente
            )
            
            # Ordenar por fecha
            df_combined = df_combined.sort_values('date').reset_index(drop=True)
            
            logger.info(f"✅ Datasets combinados: {len(df_combined)} registros totales")
            
            return df_combined
            
        except Exception as e:
            logger.error(f"❌ Error combinando datasets para {location.name}: {e}")
            return None
    
    def run_pipeline(self, 
                include_historical: bool = True,
                include_forecast: bool = True,
                create_combined: bool = True,
                locations: Optional[List[str]] = None) -> dict[str, bool]:
        """
        Ejecuta el pipeline completo de recolección de datos.
        
        Args:
            include_historical: Si incluir datos históricos
            include_forecast: Si incluir datos de pronóstico
            create_combined: Si crear archivos combinados
            locations: Lista de nombres de ubicaciones específicas (None = todas)
            
        Returns:
            dict: Reporte de éxito/fallo por ubicación
        """
        logger.info("🌍 Iniciando pipeline de recolección de datos")
        
        # Filtrar ubicaciones si se especificaron
        locations_to_process = self.config.LOCATIONS
        if locations:
            locations_to_process = [
                loc for loc in self.config.LOCATIONS 
                if loc.name in locations
            ]
            
        if not locations_to_process:
            logger.error("❌ No hay ubicaciones válidas para procesar")
            return {}
        
        results = {}
        
        for location in locations_to_process:
            logger.info(f"📍 Procesando ubicación: {location.name}")
            
            location_results = {
                'historical': False,
                'forecast': False,
                'combined': False
            }
            
            df_historical = pd.DataFrame()
            df_forecast = pd.DataFrame()
            
            # Procesar datos históricos
            if include_historical:
                if self.process_location_historical(location):
                    location_results['historical'] = True
                    df_historical = self.api_client.fetch_historical_data(location)
            
            # Procesar datos de pronóstico
            if include_forecast:
                if self.process_location_forecast(location):
                    location_results['forecast'] = True
                    df_forecast = self.api_client.fetch_forecast_data(location)
            
            # Crear dataset combinado
            if (create_combined and 
                location_results['historical'] and 
                location_results['forecast']):
                
                df_combined = self.merge_datasets(location, df_historical, df_forecast)
                
                if df_combined is not None:
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d")
                    filename = f"combined_{location.name}_{timestamp}.json"
                    output_path = Path(self.config.OUTPUT_DIR) / filename
                    
                    if self.data_utils.save_to_json(df_combined, output_path):
                        location_results['combined'] = True
                        logger.info(f"✅ Dataset combinado creado para {location.name}")
            
            results[location.name] = location_results
        
        # Reporte final
        self._print_final_report(results)
        
        return results
    
    def _print_final_report(self, results: dict[str, dict[str, bool]]) -> None:
        """
        Imprime reporte final del pipeline.
        
        Args:
            results: Resultados del pipeline por ubicación
        """
        logger.info("\n" + "="*60)
        logger.info("📊 REPORTE FINAL DEL PIPELINE")
        logger.info("="*60)
        
        total_locations = len(results)
        successful_locations = 0
        
        for location_name, location_results in results.items():
            success_count = sum(location_results.values())
            total_processes = len(location_results)
            
            if success_count > 0:
                successful_locations += 1
            
            status = "✅" if success_count == total_processes else "⚠️" if success_count > 0 else "❌"
            
            logger.info(f"{status} {location_name}: {success_count}/{total_processes} procesos exitosos")
            
            for process, success in location_results.items():
                icon = "✅" if success else "❌"
                logger.info(f"   {icon} {process}")
        
        logger.info("-" * 60)
        logger.info(f"🏁 Resumen: {successful_locations}/{total_locations} ubicaciones procesadas")
        logger.info("="*60)

def main():
    """Función principal con argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(description="Recolector de datos meteorológicos")
    
    parser.add_argument(
        "--skip-historical", 
        action="store_true", 
        help="Omitir recolección de datos históricos"
    )
    parser.add_argument(
        "--skip-forecast", 
        action="store_true", 
        help="Omitir recolección de pronósticos"
    )
    parser.add_argument(
        "--no-combined", 
        action="store_true", 
        help="No crear archivos combinados"
    )
    parser.add_argument(
        "--locations", 
        nargs="+", 
        help="Ubicaciones específicas a procesar (ej: iowa_center illinois_center)"
    )
    parser.add_argument(
        "--log-level", 
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], 
        default='INFO',
        help="Nivel de logging"
    )
    
    args = parser.parse_args()
    
    # Configurar nivel de logging
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    try:
        # Inicializar pipeline
        pipeline = WeatherDataPipeline()
        
        # Ejecutar pipeline
        results = pipeline.run_pipeline(
            include_historical=not args.skip_historical,
            include_forecast=not args.skip_forecast,
            create_combined=not args.no_combined,
            locations=args.locations
        )
        
        # Verificar si hubo algún éxito
        any_success = any(
            any(location_results.values()) 
            for location_results in results.values()
        )
        
        if any_success:
            logger.info("🎉 Pipeline completado con éxito")
            exit(0)
        else:
            logger.error("💥 Pipeline falló completamente")
            exit(1)
            
    except KeyboardInterrupt:
        logger.info("⏹️ Pipeline interrumpido por el usuario")
        exit(1)
    except Exception as e:
        logger.error(f"💥 Error crítico en el pipeline: {e}")
        exit(1)

if __name__ == "__main__":
    main()