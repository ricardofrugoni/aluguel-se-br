"""
Data processing module for cleaning and preparing Airbnb rental data.
Handles data cleaning, feature engineering, and preprocessing.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split

from config import PROCESSED_DATA_DIR


class DataProcessor:
    """
    Handles data cleaning and preprocessing for rental price prediction.
    
    Attributes:
        logger: Logger instance for tracking operations
        processed_dir: Path to processed data directory
        scaler: StandardScaler for numerical features
        label_encoders: Dictionary of LabelEncoders for categorical features
    """
    
    def __init__(self, processed_dir: Optional[Path] = None):
        """
        Initialize DataProcessor.
        
        Args:
            processed_dir: Path to processed data directory. If None, uses config default.
        """
        self.logger = logging.getLogger(__name__)
        self.processed_dir = processed_dir or PROCESSED_DATA_DIR
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        
        self.scaler = StandardScaler()
        self.label_encoders = {}
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean raw Airbnb data by removing invalid records and handling missing values.
        
        Args:
            df: Raw DataFrame to clean.
            
        Returns:
            Cleaned DataFrame.
        """
        self.logger.info("Starting data cleaning process")
        original_len = len(df)
        
        # Create a copy to avoid modifying original
        df_clean = df.copy()
        
        # Remove records with missing essential coordinates
        df_clean = df_clean.dropna(subset=['latitude', 'longitude'])
        self.logger.info(f"Removed {original_len - len(df_clean)} records with missing coordinates")
        
        # Remove records with invalid coordinates (outside reasonable bounds)
        brazil_bounds = {
            'lat_min': -33.0, 'lat_max': 5.0,
            'lon_min': -74.0, 'lon_max': -34.0
        }
        
        valid_coords = (
            (df_clean['latitude'] >= brazil_bounds['lat_min']) &
            (df_clean['latitude'] <= brazil_bounds['lat_max']) &
            (df_clean['longitude'] >= brazil_bounds['lon_min']) &
            (df_clean['longitude'] <= brazil_bounds['lon_max'])
        )
        
        df_clean = df_clean[valid_coords]
        self.logger.info(f"Removed {original_len - len(df_clean)} records with invalid coordinates")
        
        # Clean price column
        if 'price' in df_clean.columns:
            # Remove currency symbols and convert to numeric
            df_clean['price'] = df_clean['price'].astype(str).str.replace(r'[^\d.,]', '', regex=True)
            df_clean['price'] = df_clean['price'].str.replace(',', '.')
            df_clean['price'] = pd.to_numeric(df_clean['price'], errors='coerce')
            
            # Remove records with invalid prices
            df_clean = df_clean.dropna(subset=['price'])
            df_clean = df_clean[df_clean['price'] > 0]
            df_clean = df_clean[df_clean['price'] <= 10000]  # Remove extreme outliers
            
            self.logger.info(f"Price range: {df_clean['price'].min():.2f} - {df_clean['price'].max():.2f}")
        
        # Clean bedroom and bathroom columns
        for col in ['bedrooms', 'bathrooms']:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
                # Fill missing values with median
                df_clean[col] = df_clean[col].fillna(df_clean[col].median())
                # Remove extreme outliers
                df_clean = df_clean[df_clean[col] <= 10]
        
        # Clean property type
        if 'property_type' in df_clean.columns:
            # Standardize property types
            property_type_mapping = {
                'Entire home/apt': 'Entire home/apt',
                'Private room': 'Private room',
                'Shared room': 'Shared room',
                'Hotel room': 'Hotel room'
            }
            
            df_clean['property_type'] = df_clean['property_type'].map(property_type_mapping)
            df_clean['property_type'] = df_clean['property_type'].fillna('Other')
        
        # Remove duplicate records
        df_clean = df_clean.drop_duplicates()
        
        self.logger.info(f"Data cleaning completed. Records: {original_len} -> {len(df_clean)}")
        return df_clean
    
    def create_basic_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create basic features from raw data.
        
        Args:
            df: Cleaned DataFrame.
            
        Returns:
            DataFrame with basic features added.
        """
        self.logger.info("Creating basic features")
        df_features = df.copy()
        
        # Create price per bedroom feature
        if 'bedrooms' in df_features.columns and 'price' in df_features.columns:
            df_features['price_per_bedroom'] = df_features['price'] / (df_features['bedrooms'] + 1)
        
        # Create total rooms feature
        if 'bedrooms' in df_features.columns and 'bathrooms' in df_features.columns:
            df_features['total_rooms'] = df_features['bedrooms'] + df_features['bathrooms']
        
        # Create area per room feature (if area is available)
        if 'square_feet' in df_features.columns:
            df_features['area_per_room'] = df_features['square_feet'] / (df_features['total_rooms'] + 1)
        
        # Create log price for better distribution
        if 'price' in df_features.columns:
            df_features['log_price'] = np.log1p(df_features['price'])
        
        # Create city dummy variables
        if 'city' in df_features.columns:
            df_features = pd.get_dummies(df_features, columns=['city'], prefix='city')
        
        # Create property type dummy variables
        if 'property_type' in df_features.columns:
            df_features = pd.get_dummies(df_features, columns=['property_type'], prefix='property')
        
        self.logger.info(f"Created {len(df_features.columns) - len(df.columns)} new features")
        return df_features
    
    def handle_missing_values(self, df: pd.DataFrame, strategy: str = 'median') -> pd.DataFrame:
        """
        Handle missing values in the dataset.
        
        Args:
            df: DataFrame to process.
            strategy: Strategy for handling missing values ('median', 'mean', 'drop').
            
        Returns:
            DataFrame with missing values handled.
        """
        self.logger.info(f"Handling missing values with strategy: {strategy}")
        
        if strategy == 'drop':
            df_clean = df.dropna()
        elif strategy == 'median':
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df_clean = df.copy()
            df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].median())
        elif strategy == 'mean':
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df_clean = df.copy()
            df_clean[numeric_cols] = df_clean[numeric_cols].fillna(df_clean[numeric_cols].mean())
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        self.logger.info(f"Missing values handled. Shape: {df.shape} -> {df_clean.shape}")
        return df_clean
    
    def prepare_model_data(self, df: pd.DataFrame, target_col: str = 'price', 
                          test_size: float = 0.2, random_state: int = 42) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
        """
        Prepare data for machine learning models.
        
        Args:
            df: DataFrame with features.
            target_col: Name of target column.
            test_size: Proportion of data to use for testing.
            random_state: Random state for reproducibility.
            
        Returns:
            Tuple of (X_train, y_train, X_test, y_test).
        """
        self.logger.info("Preparing data for machine learning")
        
        # Separate features and target
        if target_col not in df.columns:
            raise ValueError(f"Target column '{target_col}' not found in DataFrame")
        
        # Remove non-feature columns
        feature_cols = [col for col in df.columns if col not in [target_col, 'id', 'name', 'host_id']]
        X = df[feature_cols]
        y = df[target_col]
        
        # Handle categorical variables
        categorical_cols = X.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            le = LabelEncoder()
            X[col] = le.fit_transform(X[col].astype(str))
            self.label_encoders[col] = le
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # Scale numerical features
        numerical_cols = X.select_dtypes(include=[np.number]).columns
        X_train[numerical_cols] = self.scaler.fit_transform(X_train[numerical_cols])
        X_test[numerical_cols] = self.scaler.transform(X_test[numerical_cols])
        
        self.logger.info(f"Data prepared. Train: {X_train.shape}, Test: {X_test.shape}")
        return X_train, y_train, X_test, y_test
    
    def save_processed_data(self, df: pd.DataFrame, filename: str) -> Path:
        """
        Save processed data to file.
        
        Args:
            df: DataFrame to save.
            filename: Name of the file.
            
        Returns:
            Path to saved file.
        """
        filepath = self.processed_dir / filename
        
        if filename.endswith('.csv'):
            df.to_csv(filepath, index=False)
        elif filename.endswith('.parquet'):
            df.to_parquet(filepath, index=False)
        else:
            raise ValueError("Unsupported file format. Use .csv or .parquet")
        
        self.logger.info(f"Processed data saved to {filepath}")
        return filepath
    
    def load_processed_data(self, filename: str) -> pd.DataFrame:
        """
        Load processed data from file.
        
        Args:
            filename: Name of the file to load.
            
        Returns:
            Loaded DataFrame.
        """
        filepath = self.processed_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Processed data file not found: {filepath}")
        
        if filename.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filename.endswith('.parquet'):
            df = pd.read_parquet(filepath)
        else:
            raise ValueError("Unsupported file format. Use .csv or .parquet")
        
        self.logger.info(f"Loaded processed data from {filepath}")
        return df


def main():
    """
    Example usage of DataProcessor.
    """
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize data processor
    processor = DataProcessor()
    
    # Example with sample data
    sample_data = pd.DataFrame({
        'latitude': [-23.5505, -22.9068, -23.5505],
        'longitude': [-46.6333, -43.1729, -46.6333],
        'price': [100, 150, 200],
        'bedrooms': [1, 2, 1],
        'bathrooms': [1, 1, 1],
        'property_type': ['Entire home/apt', 'Private room', 'Entire home/apt'],
        'city': ['sao_paulo', 'rio_de_janeiro', 'sao_paulo']
    })
    
    # Clean data
    cleaned_data = processor.clean_data(sample_data)
    print("Cleaned data shape:", cleaned_data.shape)
    
    # Create features
    featured_data = processor.create_basic_features(cleaned_data)
    print("Featured data shape:", featured_data.shape)
    
    # Handle missing values
    processed_data = processor.handle_missing_values(featured_data)
    print("Processed data shape:", processed_data.shape)
    
    # Prepare for modeling
    X_train, y_train, X_test, y_test = processor.prepare_model_data(processed_data)
    print("Train shape:", X_train.shape)
    print("Test shape:", X_test.shape)


if __name__ == "__main__":
    main()
