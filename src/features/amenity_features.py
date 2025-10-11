"""
Amenity feature engineering for short-term rental price prediction.
Handles amenity parsing, categorization, and scoring.
"""

import pandas as pd
import ast
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class AmenityFeatureEngineer:
    """
    Creates amenity features for short-term rental price prediction.
    
    Attributes:
        amenity_categories: Dictionary mapping category names to amenity lists
        logger: Logger instance for tracking operations
    """
    
    def __init__(self, amenity_categories: Dict[str, List[str]] = None):
        """
        Initialize AmenityFeatureEngineer.
        
        Args:
            amenity_categories: Dictionary mapping category names to amenity lists.
        """
        self.amenity_categories = amenity_categories or {}
        self.logger = logging.getLogger(__name__)
    
    def add_amenity_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Parse amenities and create amenity features.
        
        Args:
            df: DataFrame with rental data.
            
        Returns:
            DataFrame with amenity features added.
        """
        self.logger.info("Parsing and creating amenity features")
        df = df.copy()
        
        if 'amenities' not in df.columns:
            self.logger.warning("No amenities column found")
            return df
        
        # Parse amenity strings
        df['amenities_list'] = df['amenities'].apply(self._parse_amenity_string)
        df['amenities_count'] = df['amenities_list'].apply(len)
        
        # Category-based features
        for category_name, category_amenities in self.amenity_categories.items():
            df[f'has_{category_name}'] = df['amenities_list'].apply(
                lambda x: sum(1 for amenity in category_amenities 
                            if any(amenity.lower() in item.lower() for item in x))
            )
        
        # Important individual amenities
        important_amenities = {
            'wifi': ['wifi', 'internet'],
            'parking': ['parking'],
            'pool': ['pool'],
            'ac': ['air conditioning', 'heating'],
            'kitchen': ['kitchen'],
            'washer': ['washer'],
            'tv': ['tv', 'cable']
        }
        
        for amenity_name, keywords in important_amenities.items():
            df[f'has_{amenity_name}'] = df['amenities_list'].apply(
                lambda x: any(keyword.lower() in item.lower() 
                            for item in x for keyword in keywords)
            ).astype(int)
        
        # Amenity score calculation
        amenity_score_components = []
        for category in ['essential', 'premium', 'work_friendly']:
            if f'has_{category}' in df.columns:
                weight = {'essential': 0.3, 'premium': 0.5, 'work_friendly': 0.2}.get(category, 0.33)
                amenity_score_components.append(df[f'has_{category}'] * weight)
        
        if amenity_score_components:
            df['amenity_score'] = sum(amenity_score_components)
        
        self.logger.info("Amenity features created")
        return df
    
    @staticmethod
    def _parse_amenity_string(amenity_str):
        """
        Parse amenity string into list of amenities.
        
        Args:
            amenity_str: String containing amenities.
            
        Returns:
            List of amenity strings.
        """
        if pd.isna(amenity_str):
            return []
        
        try:
            return ast.literal_eval(amenity_str)
        except:
            if isinstance(amenity_str, str):
                return [item.strip() for item in amenity_str.replace('[', '').replace(']', '').replace('"', '').split(',')]
            return []


def main():
    """
    Example usage of AmenityFeatureEngineer.
    """
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize amenity feature engineer
    amenity_engineer = AmenityFeatureEngineer()
    
    # Example with sample data
    sample_data = pd.DataFrame({
        'amenities': [
            '["Wifi", "Kitchen", "Air conditioning", "TV"]',
            '["Pool", "Gym", "Elevator", "Free parking"]',
            '["Wifi", "Laptop friendly workspace", "Desk", "Printer"]'
        ]
    })
    
    # Add amenity features
    featured_data = amenity_engineer.add_amenity_features(sample_data)
    print("Amenity features added:")
    print(featured_data.columns.tolist())


if __name__ == "__main__":
    main()


