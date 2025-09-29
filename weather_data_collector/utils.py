"""
Utilidades para procesamiento y validación de datos meteorológicos.

Funciones auxiliares para guardar datos, validar DataFrames y realizar
análisis básicos de calidad de datos.
"""

import os
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import pandas as pd
import json

logger = logging.getLogger(__name__)

class DataUtils:
    """
    Utilidades para manejo y validación de datos meteorológicos.
    """
    
    @staticmethod
    def save_to_json(df: pd.DataFrame, 
                    output_path: Union[str, Path], 
                    orient: str = "records",
                    lines: bool = True,
                    date_format: str = "iso") -> bool:
        """
        Guarda el DataFrame en formato JSON con manejo robusto de errores.
        
        Args:
            df: DataFrame a guardar
            output_path: Ruta del archivo de salida
            orient: Orientación del JSON ('records', 'index', 'values', etc.)
            lines: Si usar formato JSON Lines
            date_format: Formato de fechas ('iso', 'epoch', etc.)
            
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        try:
            output_path = Path(output_path)
            
            # Crear directorio si no existe
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Validar que el DataFrame no esté vacío
            if df.empty:
                logger.warning("⚠️ DataFrame vacío, no se guardará archivo")
                return False
            
            # Guardar archivo
            df.to_json(
                output_path, 
                orient=orient, 
                lines=lines, 
                date_format=date_format,
                force_ascii=False
            )
            
            # Verificar que se guardó correctamente
            if output_path.exists() and output_path.stat().st_size > 0:
                logger.info(f"✅ Archivo JSON guardado: {output_path} ({len(df)} registros)")
                return True
            else:
                logger.error(f"❌ Error: archivo no se creó correctamente: {output_path}")
                return False
                
        except PermissionError:
            logger.error(f"❌ Sin permisos para escribir en: {output_path}")
            return False
        except Exception as e:
            logger.error(f"❌ Error guardando JSON en {output_path}: {e}")
            return False
    
    @staticmethod
    def save_to_csv(df: pd.DataFrame, 
                   output_path: Union[str, Path],
                   index: bool = False) -> bool:
        """
        Guarda el DataFrame en formato CSV.
        
        Args:
            df: DataFrame a guardar
            output_path: Ruta del archivo de salida
            index: Si incluir el índice en el archivo
            
        Returns:
            bool: True si se guardó correctamente
        """
        try:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if df.empty:
                logger.warning("⚠️ DataFrame vacío, no se guardará CSV")
                return False
            
            df.to_csv(output_path, index=index)
            logger.info(f"✅ Archivo CSV guardado: {output_path} ({len(df)} registros)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error guardando CSV en {output_path}: {e}")
            return False
    
    @staticmethod
    def preview_data(df: pd.DataFrame, n: int = 5) -> None:
        """
        Muestra información resumida del DataFrame.
        
        Args:
            df: DataFrame a previsualizar
            n: Número de filas a mostrar
        """
        if df.empty:
            print("DataFrame vacío")
            return
        
        print(f"📊 Vista previa de datos ({len(df)} registros total):")
        print("-" * 60)
        print(df.head(n))
        print(f"ℹ️ Forma: {df.shape} | Columnas: {list(df.columns)}")
        
        # Mostrar tipos de datos
        print("📋 Tipos de datos:")
        for col, dtype in df.dtypes.items():
            null_count = df[col].isnull().sum()
            null_pct = (null_count / len(df)) * 100
            print(f"  {col}: {dtype} (nulos: {null_count}, {null_pct:.1f}%)")
    
    @staticmethod
    def validate_columns(df: pd.DataFrame, 
                        expected_columns: List[str],
                        strict: bool = False) -> bool:
        """
        Valida las columnas del DataFrame.
        
        Args:
            df: DataFrame a validar
            expected_columns: Lista de columnas esperadas
            strict: Si True, no permite columnas adicionales
            
        Returns:
            bool: True si la validación pasa
        """
        if df.empty:
            logger.warning("⚠️ No se puede validar DataFrame vacío")
            return False
        
        # Verificar columnas faltantes
        missing = [col for col in expected_columns if col not in df.columns]
        if missing:
            logger.error(f"❌ Faltan columnas requeridas: {missing}")
            return False
        
        # Verificar columnas extra (solo en modo strict)
        if strict:
            extra = [col for col in df.columns if col not in expected_columns]
            if extra:
                logger.error(f"❌ Columnas no esperadas: {extra}")
                return False
        
        logger.info("✅ Validación de columnas exitosa")
        return True
    
    @staticmethod
    def validate_data_quality(df: pd.DataFrame, 
                            location_name: str = "unknown") -> Dict[str, Any]:
        """
        Realiza validación de calidad de datos meteorológicos.
        
        Args:
            df: DataFrame a validar
            location_name: Nombre de la ubicación para logging
            
        Returns:
            dict: Reporte de calidad de datos
        """
        if df.empty:
            return {"status": "error", "message": "DataFrame vacío"}
        
        logger.info(f"Validando calidad de datos para {location_name}")
        
        report = {
            "location": location_name,
            "total_records": len(df),
            "date_range": None,
            "missing_data": {},
            "data_issues": [],
            "status": "ok"
        }
        
        # Validar fechas
        if 'date' in df.columns:
            try:
                df['date'] = pd.to_datetime(df['date'])
                report["date_range"] = {
                    "start": df['date'].min().strftime("%Y-%m-%d"),
                    "end": df['date'].max().strftime("%Y-%m-%d")
                }
            except Exception as e:
                report["data_issues"].append(f"Error en fechas: {e}")
        
        # Validar valores faltantes
        for col in df.columns:
            null_count = df[col].isnull().sum()
            if null_count > 0:
                null_pct = (null_count / len(df)) * 100
                report["missing_data"][col] = {
                    "count": null_count,
                    "percentage": round(null_pct, 2)
                }
                
                if null_pct > 10:  # Más del 10% de datos faltantes
                    report["data_issues"].append(
                        f"{col}: {null_pct:.1f}% datos faltantes"
                    )
        
        # Validar rangos de temperatura (si existen)
        temp_cols = ['temperature_2m_max', 'temperature_2m_min']
        for col in temp_cols:
            if col in df.columns:
                values = df[col].dropna()
                if not values.empty:
                    if (values < -50).any() or (values > 60).any():
                        report["data_issues"].append(
                            f"{col}: valores fuera de rango (-50°C a 60°C)"
                        )
        
        # Status final
        if report["data_issues"]:
            report["status"] = "warning"
            logger.warning(f"⚠️ Problemas de calidad encontrados: {len(report['data_issues'])}")
        else:
            logger.info("✅ Calidad de datos validada correctamente")
        
        return report
    
    @staticmethod
    def generate_filename(location_name: str, 
                         data_type: str = "weather",
                         extension: str = "json") -> str:
        """
        Genera nombre de archivo estandarizado.
        
        Args:
            location_name: Nombre de la ubicación
            data_type: Tipo de datos ('weather', 'forecast', etc.)
            extension: Extensión del archivo
            
        Returns:
            str: Nombre de archivo generado
        """
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d")
        clean_location = location_name.lower().replace(" ", "_")
        
        return f"{data_type}_{clean_location}_{timestamp}.{extension}"
    
    @staticmethod
    def load_json_data(file_path: Union[str, Path]) -> Optional[pd.DataFrame]:
        """
        Carga datos desde archivo JSON.
        
        Args:
            file_path: Ruta del archivo JSON
            
        Returns:
            pd.DataFrame or None: Datos cargados o None si hay error
        """
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                logger.error(f"❌ Archivo no encontrado: {file_path}")
                return None
            
            # Detectar si es JSON Lines o JSON normal
            with open(file_path, 'r') as f:
                first_line = f.readline().strip()
            
            if first_line.startswith('['):
                # JSON normal
                df = pd.read_json(file_path)
            else:
                # JSON Lines
                df = pd.read_json(file_path, lines=True)
            
            logger.info(f"✅ Archivo cargado: {file_path} ({len(df)} registros)")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error cargando JSON desde {file_path}: {e}")
            return None

# Funciones de conveniencia para mantener compatibilidad
def save_to_json(df: pd.DataFrame, output_path: str) -> None:
    """Función de compatibilidad - DEPRECATED"""
    logger.warning("⚠️ Usando función deprecated. Considera migrar a DataUtils.save_to_json()")
    DataUtils.save_to_json(df, output_path)

def preview_data(df: pd.DataFrame, n: int = 5) -> None:
    """Función de compatibilidad - DEPRECATED"""
    logger.warning("⚠️ Usando función deprecated. Considera migrar a DataUtils.preview_data()")
    DataUtils.preview_data(df, n)

def validate_columns(df: pd.DataFrame, expected_columns: list) -> bool:
    """Función de compatibilidad - DEPRECATED"""
    logger.warning("⚠️ Usando función deprecated. Considera migrar a DataUtils.validate_columns()")
    return DataUtils.validate_columns(df, expected_columns)