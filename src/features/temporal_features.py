"""
Temporal feature engineering for short-term rental price prediction.
Handles seasonal patterns, holidays, and booking patterns.
"""

import pandas as pd
import numpy as np
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)


class TemporalFeatureEngineer:
    """
    Creates temporal features for short-term rental price prediction.
    
    Attributes:
        holidays: List of holiday tuples (month, day)
        logger: Logger instance for tracking operations
    """
    
    def __init__(self, holidays: List[Tuple[int, int]] = None):
        """
        Initialize TemporalFeatureEngineer.
        
        Args:
            holidays: List of holiday tuples (month, day). If None, uses default holidays.
        """
        self.holidays = holidays or []
        self.logger = logging.getLogger(__name__)
    
    def add_all_temporal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add all temporal features to the dataset.
        
        Args:
            df: DataFrame with rental data.
            
        Returns:
            DataFrame with temporal features added.
        """
        self.logger.info("Adding all temporal features")
        df = df.copy()
        
        df = self.add_date_features(df)
        df = self.add_seasonal_features(df)
        df = self.add_booking_patterns(df)
        
        self.logger.info(f"Temporal features added. Total columns: {len(df.columns)}")
        return df
    
    def add_date_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add date-based features.
        
        Args:
            df: DataFrame with rental data.
            
        Returns:
            DataFrame with date features added.
        """
        df = df.copy()
        
        # Current date features
        df['current_date'] = pd.to_datetime('today')
        df['month'] = df['current_date'].dt.month
        df['day_of_week'] = df['current_date'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        
        # Cyclical encoding for temporal features
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        df['day_sin'] = np.sin(2 * np.pi * df['day_of_week'] / 7)
        df['day_cos'] = np.cos(2 * np.pi * df['day_of_week'] / 7)
        
        return df
    
    def add_seasonal_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add seasonal features.
        
        Args:
            df: DataFrame with rental data.
            
        Returns:
            DataFrame with seasonal features added.
        """
        df = df.copy()
        
        if 'month' not in df.columns:
            df['month'] = pd.to_datetime('today').month
        
        # Season mapping for Brazil (Southern Hemisphere)
        df['season'] = df['month'].apply(self._get_season)
        df['is_high_season'] = df['season'].isin(['summer']).astype(int)
        df['quarter'] = df['month'].apply(lambda m: (m - 1) // 3 + 1)
        
        return df
    
    def add_booking_patterns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add booking pattern features.
        
        Args:
            df: DataFrame with rental data.
            
        Returns:
            DataFrame with booking pattern features added.
        """
        df = df.copy()
        
        # Occupancy rate features
        if 'availability_30' in df.columns:
            df['occupancy_rate_30'] = (1 - (df['availability_30'] / 30)).clip(0, 1)
        
        if 'availability_60' in df.columns:
            df['occupancy_rate_60'] = (1 - (df['availability_60'] / 60)).clip(0, 1)
        
        if 'availability_90' in df.columns:
            df['occupancy_rate_90'] = (1 - (df['availability_90'] / 90)).clip(0, 1)
        
        # Review-based demand indicators
        if 'reviews_per_month' in df.columns:
            df['recent_demand'] = df['reviews_per_month'].fillna(0)
        
        # Popularity score combining reviews and demand
        if 'number_of_reviews' in df.columns and 'reviews_per_month' in df.columns:
            df['popularity_score'] = (
                df['number_of_reviews'].fillna(0) * 0.5 + 
                df['reviews_per_month'].fillna(0) * 100 * 0.5
            )
        
        return df
    
    @staticmethod
    def _get_season(month: int) -> str:
        """
        Get season for a given month (Brazil - Southern Hemisphere).
        
        Args:
            month: Month number (1-12).
            
        Returns:
            Season name.
        """
        if month in [12, 1, 2]:
            return 'summer'
        elif month in [3, 4, 5]:
            return 'autumn'
        elif month in [6, 7, 8]:
            return 'winter'
        else:
            return 'spring'


def main():
    """
    Example usage of TemporalFeatureEngineer.
    """
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize temporal feature engineer
    temporal_engineer = TemporalFeatureEngineer()
    
    # Example with sample data
    sample_data = pd.DataFrame({
        'availability_30': [10, 5, 20],
        'availability_60': [20, 10, 40],
        'availability_90': [30, 15, 60],
        'reviews_per_month': [2.5, 1.0, 4.0],
        'number_of_reviews': [50, 20, 100]
    })
    
    # Add temporal features
    featured_data = temporal_engineer.add_all_temporal_features(sample_data)
    print("Temporal features added:")
    print(featured_data.columns.tolist())


if __name__ == "__main__":
    main()
