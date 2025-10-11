"""
Unit tests for data loading module.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil

from src.data.data_loader import DataLoader


class TestDataLoader:
    """Test cases for DataLoader class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.loader = DataLoader(self.temp_dir)
        
        # Create sample data for testing
        self.sample_data = pd.DataFrame({
            'latitude': [-23.5505, -22.9068, -23.5505],
            'longitude': [-46.6333, -43.1729, -46.6333],
            'price': [100, 150, 200],
            'bedrooms': [1, 2, 1],
            'bathrooms': [1, 1, 1],
            'property_type': ['Entire home/apt', 'Private room', 'Entire home/apt']
        })
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_validate_data(self):
        """Test data validation functionality."""
        # Test with valid data
        validation_results = self.loader.validate_data(self.sample_data)
        
        assert validation_results['total_records'] == 3
        assert validation_results['total_columns'] == 6
        assert 'missing_values' in validation_results
        assert 'duplicate_records' in validation_results
    
    def test_validate_data_missing_columns(self):
        """Test data validation with missing required columns."""
        # Remove required columns
        invalid_data = self.sample_data.drop(columns=['latitude', 'longitude'])
        
        validation_results = self.loader.validate_data(invalid_data)
        
        assert 'missing_required_columns' in validation_results
        assert 'latitude' in validation_results['missing_required_columns']
        assert 'longitude' in validation_results['missing_required_columns']
    
    def test_validate_data_out_of_bounds(self):
        """Test data validation with out-of-bounds coordinates."""
        # Create data with coordinates outside Brazil
        out_of_bounds_data = self.sample_data.copy()
        out_of_bounds_data['latitude'] = [50.0, 60.0, 70.0]  # Outside Brazil
        
        validation_results = self.loader.validate_data(out_of_bounds_data)
        
        assert 'coordinate_warnings' in validation_results
    
    def test_get_data_summary(self):
        """Test data summary generation."""
        summary = self.loader.get_data_summary(self.sample_data)
        
        assert summary['shape'] == (3, 6)
        assert 'memory_usage_mb' in summary
        assert 'numeric_columns' in summary
        assert 'categorical_columns' in summary
        assert 'price_stats' in summary
    
    def test_get_data_summary_price_stats(self):
        """Test price statistics in data summary."""
        summary = self.loader.get_data_summary(self.sample_data)
        price_stats = summary['price_stats']
        
        assert price_stats['count'] == 3
        assert price_stats['mean'] == 150.0
        assert price_stats['median'] == 150.0
        assert price_stats['min'] == 100.0
        assert price_stats['max'] == 200.0
        assert price_stats['missing'] == 0
    
    def test_load_multiple_cities(self):
        """Test loading multiple cities."""
        # This test would require actual data files, so we'll test the method structure
        cities = ['sao_paulo', 'rio_de_janeiro']
        
        # Test with empty data (since we don't have actual files)
        try:
            result = self.loader.load_multiple_cities(cities)
            # This should raise an error since files don't exist
            assert False, "Expected FileNotFoundError"
        except FileNotFoundError:
            # This is expected behavior
            pass
    
    def test_download_data_invalid_city(self):
        """Test downloading data for invalid city."""
        with pytest.raises(ValueError):
            self.loader.download_data(['invalid_city'])
    
    def test_load_raw_data_file_not_found(self):
        """Test loading raw data when file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            self.loader.load_raw_data('nonexistent_city')
    
    def test_data_loader_initialization(self):
        """Test DataLoader initialization."""
        assert self.loader.data_dir == self.temp_dir
        assert self.loader.logger is not None
    
    def test_data_loader_custom_data_dir(self):
        """Test DataLoader with custom data directory."""
        custom_dir = Path(tempfile.mkdtemp())
        loader = DataLoader(custom_dir)
        
        assert loader.data_dir == custom_dir
        assert custom_dir.exists()
        
        # Clean up
        shutil.rmtree(custom_dir)


if __name__ == "__main__":
    pytest.main([__file__])


