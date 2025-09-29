"""
Tests unitarios para el módulo de utilidades.

Valida funciones de guardado, carga y validación de datos meteorológicos.
"""

import pytest
import pandas as pd
import tempfile
import os
from pathlib import Path
import json

from weather_data_collector.utils import DataUtils
from weather_data_collector.config import Location

class TestDataUtils:
    """Tests para la clase DataUtils"""
    
    def setup_method(self):
        """Preparar datos de prueba para cada test"""
        # DataFrame de ejemplo
        self.sample_df = pd.DataFrame({
            'date': ['2025-01-01', '2025-01-02', '2025-01-03'],
            'location': ['test_location', 'test_location', 'test_location'],
            'temperature_2m_max': [25.5, 26.0, 24.8],
            'temperature_2m_min': [15.2, 16.1, 14.9],
            'precipitation_sum': [0.0, 2.5, 0.1]
        })
        
        # DataFrame vacío para tests
        self.empty_df = pd.DataFrame()
        
        # Directorio temporal
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Limpiar después de cada test"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_save_to_json_success(self):
        """Test guardar JSON exitosamente"""
        output_path = Path(self.temp_dir) / "test_weather.json"
        
        result = DataUtils.save_to_json(self.sample_df, output_path)
        
        assert result == True
        assert output_path.exists()
        
        # Verificar contenido
        with open(output_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 3  # 3 registros
    
    def test_save_to_json_empty_dataframe(self):
        """Test guardar DataFrame vacío retorna False"""
        output_path = Path(self.temp_dir) / "empty.json"
        
        result = DataUtils.save_to_json(self.empty_df, output_path)
        
        assert result == False
        assert not output_path.exists()
    
    def test_save_to_csv_success(self):
        """Test guardar CSV exitosamente"""
        output_path = Path(self.temp_dir) / "test_weather.csv"
        
        result = DataUtils.save_to_csv(self.sample_df, output_path)
        
        assert result == True
        assert output_path.exists()
        
        # Verificar que se puede cargar
        loaded_df = pd.read_csv(output_path)
        assert len(loaded_df) == 3
    
    def test_validate_columns_success(self):
        """Test validación de columnas exitosa"""
        expected_columns = ['date', 'location', 'temperature_2m_max']
        
        result = DataUtils.validate_columns(self.sample_df, expected_columns)
        
        assert result == True
    
    def test_validate_columns_missing(self):
        """Test validación falla con columnas faltantes"""
        expected_columns = ['date', 'location', 'nonexistent_column']
        
        result = DataUtils.validate_columns(self.sample_df, expected_columns)
        
        assert result == False
    
    def test_validate_columns_strict_mode(self):
        """Test validación estricta rechaza columnas extra"""
        expected_columns = ['date', 'location']  # Faltan columnas
        
        result = DataUtils.validate_columns(self.sample_df, expected_columns, strict=True)
        
        assert result == False
    
    def test_validate_data_quality_success(self):
        """Test validación de calidad exitosa"""
        report = DataUtils.validate_data_quality(self.sample_df, "test_location")
        
        assert report["status"] in ["ok", "warning"]
        assert report["location"] == "test_location"
        assert report["total_records"] == 3
        assert "date_range" in report
    
    def test_validate_data_quality_empty_dataframe(self):
        """Test validación de DataFrame vacío"""
        report = DataUtils.validate_data_quality(self.empty_df, "empty")
        
        assert report["status"] == "error"
        assert "DataFrame vacío" in report["message"]
    
    def test_validate_data_quality_extreme_temperatures(self):
        """Test validación detecta temperaturas extremas"""
        # DataFrame con temperaturas extremas
        bad_df = pd.DataFrame({
            'date': ['2025-01-01'],
            'location': ['extreme_location'],
            'temperature_2m_max': [70.0],  # Temperatura muy alta
            'temperature_2m_min': [-60.0]   # Temperatura muy baja
        })
        
        report = DataUtils.validate_data_quality(bad_df, "extreme_location")
        
        assert report["status"] == "warning"
        assert len(report["data_issues"]) > 0
    
    def test_generate_filename(self):
        """Test generación de nombres de archivo"""
        filename = DataUtils.generate_filename("test location", "weather", "json")
        
        assert "weather_test_location_" in filename
        assert filename.endswith(".json")
        assert " " not in filename  # Sin espacios
    
    def test_load_json_data_success(self):
        """Test cargar datos JSON exitosamente"""
        # Primero guardar un archivo
        output_path = Path(self.temp_dir) / "test_load.json"
        DataUtils.save_to_json(self.sample_df, output_path)
        
        # Luego cargarlo
        loaded_df = DataUtils.load_json_data(output_path)
        
        assert loaded_df is not None
        assert len(loaded_df) == 3
        assert 'location' in loaded_df.columns
    
    def test_load_json_data_file_not_found(self):
        """Test cargar archivo inexistente retorna None"""
        nonexistent_path = Path(self.temp_dir) / "nonexistent.json"
        
        result = DataUtils.load_json_data(nonexistent_path)
        
        assert result is None
    
    def test_preview_data_with_data(self):
        """Test previsualización con datos (no genera errores)"""
        # Este test solo verifica que no genere errores
        try:
            DataUtils.preview_data(self.sample_df, n=2)
            success = True
        except Exception:
            success = False
        
        assert success == True
    
    def test_preview_data_empty(self):
        """Test previsualización con DataFrame vacío"""
        try:
            DataUtils.preview_data(self.empty_df)
            success = True
        except Exception:
            success = False
        
        assert success == True

if __name__ == "__main__":
    # Permitir ejecutar tests directamente
    pytest.main([__file__, "-v"])