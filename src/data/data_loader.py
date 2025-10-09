"""
Data loading module for Airbnb rental data.
Handles downloading, loading, and basic validation of raw data.
"""

import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.request import urlretrieve
import gzip
import shutil

from config import RAW_DATA_DIR, AIRBNB_DATA_URLS


class DataLoader:
    """
    Handles loading and basic processing of Airbnb rental data.
    
    Attributes:
        logger: Logger instance for tracking operations
        data_dir: Path to raw data directory
    """
    
    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize DataLoader.
        
        Args:
            data_dir: Path to data directory. If None, uses config default.
        """
        self.logger = logging.getLogger(__name__)
        self.data_dir = data_dir or RAW_DATA_DIR
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def download_data(self, cities: Optional[List[str]] = None) -> Dict[str, Path]:
        """
        Download Airbnb data for specified cities.
        
        Args:
            cities: List of city names to download. If None, downloads all.
            
        Returns:
            Dictionary mapping city names to file paths.
            
        Raises:
            ValueError: If city name is not supported.
            ConnectionError: If download fails.
        """
        if cities is None:
            cities = list(AIRBNB_DATA_URLS.keys())
        
        downloaded_files = {}
        
        for city in cities:
            if city not in AIRBNB_DATA_URLS:
                raise ValueError(f"City '{city}' not supported. Available: {list(AIRBNB_DATA_URLS.keys())}")
            
            url = AIRBNB_DATA_URLS[city]
            filename = f"{city}_listings.csv.gz"
            filepath = self.data_dir / filename
            
            self.logger.info(f"Downloading data for {city} from {url}")
            
            try:
                urlretrieve(url, filepath)
                self.logger.info(f"Successfully downloaded {filename}")
                downloaded_files[city] = filepath
                
            except Exception as e:
                self.logger.error(f"Failed to download data for {city}: {e}")
                raise ConnectionError(f"Failed to download data for {city}") from e
        
        return downloaded_files
    
    def load_raw_data(self, city: str, filepath: Optional[Path] = None) -> pd.DataFrame:
        """
        Load raw Airbnb data for a specific city.
        
        Args:
            city: City name
            filepath: Path to data file. If None, uses default naming.
            
        Returns:
            DataFrame with raw Airbnb data.
            
        Raises:
            FileNotFoundError: If data file doesn't exist.
            ValueError: If data cannot be loaded.
        """
        if filepath is None:
            filepath = self.data_dir / f"{city}_listings.csv.gz"
        
        if not filepath.exists():
            raise FileNotFoundError(f"Data file not found: {filepath}")
        
        self.logger.info(f"Loading raw data from {filepath}")
        
        try:
            # Handle compressed files
            if filepath.suffix == '.gz':
                with gzip.open(filepath, 'rt', encoding='utf-8') as f:
                    df = pd.read_csv(f, low_memory=False)
            else:
                df = pd.read_csv(filepath, low_memory=False)
            
            self.logger.info(f"Loaded {len(df)} records with {len(df.columns)} columns")
            return df
            
        except Exception as e:
            self.logger.error(f"Failed to load data from {filepath}: {e}")
            raise ValueError(f"Failed to load data from {filepath}") from e
    
    def load_multiple_cities(self, cities: List[str]) -> pd.DataFrame:
        """
        Load and combine data from multiple cities.
        
        Args:
            cities: List of city names to load.
            
        Returns:
            Combined DataFrame with data from all cities.
        """
        dataframes = []
        
        for city in cities:
            self.logger.info(f"Loading data for {city}")
            df = self.load_raw_data(city)
            df['city'] = city  # Add city identifier
            dataframes.append(df)
        
        combined_df = pd.concat(dataframes, ignore_index=True)
        self.logger.info(f"Combined data: {len(combined_df)} total records")
        
        return combined_df
    
    def validate_data(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Perform basic data validation.
        
        Args:
            df: DataFrame to validate.
            
        Returns:
            Dictionary with validation results.
        """
        validation_results = {
            'total_records': len(df),
            'total_columns': len(df.columns),
            'missing_values': df.isnull().sum().to_dict(),
            'duplicate_records': df.duplicated().sum(),
            'data_types': df.dtypes.to_dict()
        }
        
        # Check for required columns
        required_columns = ['latitude', 'longitude', 'price', 'bedrooms', 'bathrooms']
        missing_required = [col for col in required_columns if col not in df.columns]
        
        if missing_required:
            self.logger.warning(f"Missing required columns: {missing_required}")
            validation_results['missing_required_columns'] = missing_required
        
        # Check for reasonable coordinate ranges (Brazil bounds)
        if 'latitude' in df.columns and 'longitude' in df.columns:
            lat_range = (df['latitude'].min(), df['latitude'].max())
            lon_range = (df['longitude'].min(), df['longitude'].max())
            
            # Brazil approximate bounds
            brazil_bounds = {
                'lat_min': -33.0, 'lat_max': 5.0,
                'lon_min': -74.0, 'lon_max': -34.0
            }
            
            out_of_bounds = (
                lat_range[0] < brazil_bounds['lat_min'] or 
                lat_range[1] > brazil_bounds['lat_max'] or
                lon_range[0] < brazil_bounds['lon_min'] or 
                lon_range[1] > brazil_bounds['lon_max']
            )
            
            if out_of_bounds:
                self.logger.warning("Some coordinates appear to be outside Brazil bounds")
                validation_results['coordinate_warnings'] = {
                    'lat_range': lat_range,
                    'lon_range': lon_range,
                    'brazil_bounds': brazil_bounds
                }
        
        self.logger.info("Data validation completed")
        return validation_results
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Generate summary statistics for the dataset.
        
        Args:
            df: DataFrame to summarize.
            
        Returns:
            Dictionary with summary statistics.
        """
        summary = {
            'shape': df.shape,
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024**2,
            'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': df.select_dtypes(include=['object']).columns.tolist(),
            'date_columns': df.select_dtypes(include=['datetime']).columns.tolist()
        }
        
        # Price statistics if available
        if 'price' in df.columns:
            price_series = pd.to_numeric(df['price'], errors='coerce')
            summary['price_stats'] = {
                'count': price_series.count(),
                'mean': price_series.mean(),
                'median': price_series.median(),
                'std': price_series.std(),
                'min': price_series.min(),
                'max': price_series.max(),
                'missing': price_series.isnull().sum()
            }
        
        return summary


def main():
    """
    Example usage of DataLoader.
    """
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize data loader
    loader = DataLoader()
    
    # Download data for São Paulo and Rio de Janeiro
    try:
        downloaded_files = loader.download_data(['sao_paulo', 'rio_de_janeiro'])
        print("Downloaded files:", downloaded_files)
        
        # Load and validate data
        df = loader.load_multiple_cities(['sao_paulo', 'rio_de_janeiro'])
        
        # Validate data
        validation_results = loader.validate_data(df)
        print("Validation results:", validation_results)
        
        # Get summary
        summary = loader.get_data_summary(df)
        print("Data summary:", summary)
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
