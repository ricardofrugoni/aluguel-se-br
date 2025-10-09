"""
Feature engineering module for creating geospatial features.
Handles distance calculations, density features, and grid-based aggregations.
"""

import logging
import pandas as pd
import numpy as np
import geopandas as gpd
from typing import Dict, List, Optional, Tuple, Union
from pathlib import Path
from sklearn.neighbors import BallTree
from shapely.geometry import Point
import math

from config import GRID_SIZE, DENSITY_RADIUS_KM, DISTANCE_THRESHOLD_KM, AMENITY_CATEGORIES, MIN_REVIEWS_FOR_TRUST, MAJOR_HOLIDAYS
from src.features.temporal_features import TemporalFeatureEngineer
from src.features.review_features import ReviewFeatureEngineer
from src.features.amenity_features import AmenityFeatureEngineer


class FeatureEngineer:
    """
    Creates geospatial features for rental price prediction.
    
    Attributes:
        logger: Logger instance for tracking operations
        grid_size: Size of grid cells in degrees
        density_radius: Radius for density calculations in km
        distance_threshold: Maximum distance to consider for POI distances
    """
    
    def __init__(self, grid_size: float = GRID_SIZE, density_radius_km: float = DENSITY_RADIUS_KM,
                 distance_threshold_km: float = DISTANCE_THRESHOLD_KM):
        """
        Initialize FeatureEngineer.
        
        Args:
            grid_size: Size of grid cells in degrees.
            density_radius_km: Radius for density calculations in km.
            distance_threshold_km: Maximum distance to consider for POI distances.
        """
        self.logger = logging.getLogger(__name__)
        self.grid_size = grid_size
        self.density_radius_km = density_radius_km
        self.distance_threshold_km = distance_threshold_km
    
    def calculate_distances(self, df: pd.DataFrame, pois: Dict[str, gpd.GeoDataFrame]) -> pd.DataFrame:
        """
        Calculate distances from each property to nearest POIs.
        
        Args:
            df: DataFrame with property data (must have 'latitude', 'longitude' columns).
            pois: Dictionary mapping POI types to GeoDataFrames.
            
        Returns:
            DataFrame with distance features added.
        """
        self.logger.info("Calculating distance features")
        
        # Create a copy to avoid modifying original
        df_with_distances = df.copy()
        
        # Convert property coordinates to radians for BallTree
        property_coords = np.radians(df[['latitude', 'longitude']].values)
        
        for poi_type, poi_gdf in pois.items():
            if len(poi_gdf) == 0:
                self.logger.warning(f"No {poi_type} POIs available, setting distances to NaN")
                df_with_distances[f'dist_nearest_{poi_type}_km'] = np.nan
                continue
            
            # Convert POI coordinates to radians
            poi_coords = np.radians(poi_gdf[['latitude', 'longitude']].values)
            
            # Create BallTree for efficient distance calculations
            tree = BallTree(poi_coords, metric='haversine')
            
            # Calculate distances to nearest POI
            distances, indices = tree.query(property_coords, k=1)
            
            # Convert from radians to kilometers (Earth radius = 6371 km)
            distances_km = distances.flatten() * 6371
            
            # Set distances beyond threshold to NaN
            distances_km[distances_km > self.distance_threshold_km] = np.nan
            
            df_with_distances[f'dist_nearest_{poi_type}_km'] = distances_km
            
            self.logger.info(f"Calculated distances to {poi_type} POIs")
        
        return df_with_distances
    
    def calculate_densities(self, df: pd.DataFrame, pois: Dict[str, gpd.GeoDataFrame]) -> pd.DataFrame:
        """
        Calculate POI densities within specified radius.
        
        Args:
            df: DataFrame with property data.
            pois: Dictionary mapping POI types to GeoDataFrames.
            
        Returns:
            DataFrame with density features added.
        """
        self.logger.info("Calculating density features")
        
        # Create a copy to avoid modifying original
        df_with_densities = df.copy()
        
        # Convert property coordinates to radians
        property_coords = np.radians(df[['latitude', 'longitude']].values)
        
        # Convert radius from km to radians
        radius_radians = self.density_radius_km / 6371
        
        for poi_type, poi_gdf in pois.items():
            if len(poi_gdf) == 0:
                self.logger.warning(f"No {poi_type} POIs available, setting densities to 0")
                df_with_densities[f'count_{poi_type}_1km'] = 0
                continue
            
            # Convert POI coordinates to radians
            poi_coords = np.radians(poi_gdf[['latitude', 'longitude']].values)
            
            # Create BallTree for efficient radius queries
            tree = BallTree(poi_coords, metric='haversine')
            
            # Count POIs within radius
            counts = tree.query_radius(property_coords, r=radius_radians, count_only=True)
            
            df_with_densities[f'count_{poi_type}_1km'] = counts
            
            self.logger.info(f"Calculated densities for {poi_type} POIs")
        
        return df_with_densities
    
    def create_grid_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create grid-based features by aggregating data within grid cells.
        
        Args:
            df: DataFrame with property data.
            
        Returns:
            DataFrame with grid features added.
        """
        self.logger.info("Creating grid features")
        
        # Create a copy to avoid modifying original
        df_with_grid = df.copy()
        
        # Create grid coordinates
        df_with_grid['grid_lat'] = (df_with_grid['latitude'] / self.grid_size).round() * self.grid_size
        df_with_grid['grid_lon'] = (df_with_grid['longitude'] / self.grid_size).round() * self.grid_size
        
        # Create grid identifier
        df_with_grid['grid_id'] = (df_with_grid['grid_lat'].astype(str) + '_' + 
                                  df_with_grid['grid_lon'].astype(str))
        
        # Calculate grid-based aggregations
        grid_features = df_with_grid.groupby('grid_id').agg({
            'price': ['mean', 'median', 'std', 'count'],
            'bedrooms': ['mean', 'median'],
            'bathrooms': ['mean', 'median']
        }).reset_index()
        
        # Flatten column names
        grid_features.columns = ['grid_id'] + [f'grid_{col[0]}_{col[1]}' for col in grid_features.columns[1:]]
        
        # Merge grid features back to main dataframe
        df_with_grid = df_with_grid.merge(grid_features, on='grid_id', how='left')
        
        # Fill missing values with overall statistics
        for col in grid_features.columns[1:]:
            if col in df_with_grid.columns:
                df_with_grid[col] = df_with_grid[col].fillna(df_with_grid[col].median())
        
        self.logger.info(f"Created {len(grid_features.columns) - 1} grid features")
        return df_with_grid
    
    def create_accessibility_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create accessibility and transport scores based on POI distances.
        
        Args:
            df: DataFrame with distance features.
            
        Returns:
            DataFrame with accessibility scores added.
        """
        self.logger.info("Creating accessibility scores")
        
        # Create a copy to avoid modifying original
        df_with_scores = df.copy()
        
        # Get distance columns
        distance_cols = [col for col in df.columns if col.startswith('dist_nearest_')]
        
        if not distance_cols:
            self.logger.warning("No distance features found, skipping accessibility scores")
            return df_with_scores
        
        # Create accessibility score (inverse of average distance)
        distances = df[distance_cols].values
        # Replace NaN with large distance for calculation
        distances_filled = np.nan_to_num(distances, nan=self.distance_threshold_km)
        
        # Calculate average distance (excluding zeros)
        valid_distances = distances_filled > 0
        avg_distances = np.where(valid_distances.any(axis=1),
                                np.nanmean(distances_filled, axis=1),
                                self.distance_threshold_km)
        
        # Accessibility score (higher is better)
        df_with_scores['accessibility_score'] = 1 / (avg_distances + 0.1)  # Add small constant to avoid division by zero
        
        # Transport score (based on subway distance)
        subway_col = 'dist_nearest_subway_km'
        if subway_col in df.columns:
            subway_distances = df[subway_col].fillna(self.distance_threshold_km)
            df_with_scores['transport_score'] = 1 / (subway_distances + 0.1)
        else:
            df_with_scores['transport_score'] = 0
        
        self.logger.info("Created accessibility and transport scores")
        return df_with_scores
    
    def create_interaction_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create interaction features between different variables.
        
        Args:
            df: DataFrame with basic features.
            
        Returns:
            DataFrame with interaction features added.
        """
        self.logger.info("Creating interaction features")
        
        # Create a copy to avoid modifying original
        df_with_interactions = df.copy()
        
        # Price per bedroom interaction with accessibility
        if 'price_per_bedroom' in df.columns and 'accessibility_score' in df.columns:
            df_with_interactions['price_per_bedroom_accessibility'] = (
                df_with_interactions['price_per_bedroom'] * df_with_interactions['accessibility_score']
            )
        
        # Bedroom-bathroom interaction
        if 'bedrooms' in df.columns and 'bathrooms' in df.columns:
            df_with_interactions['bedroom_bathroom_ratio'] = (
                df_with_interactions['bedrooms'] / (df_with_interactions['bathrooms'] + 0.1)
            )
        
        # Distance to transport vs. price interaction
        if 'dist_nearest_subway_km' in df.columns and 'price' in df.columns:
            df_with_interactions['price_transport_interaction'] = (
                df_with_interactions['price'] * df_with_interactions['dist_nearest_subway_km']
            )
        
        self.logger.info("Created interaction features")
        return df_with_interactions
    
    def create_all_features(self, df: pd.DataFrame, pois: Dict = None) -> pd.DataFrame:
        """
        Create all features including geospatial, temporal, reviews, and amenities.
        
        Args:
            df: DataFrame with property data.
            pois: Dictionary mapping POI types to GeoDataFrames.
            
        Returns:
            DataFrame with all features added.
        """
        self.logger.info("Creating all features including geospatial, temporal, reviews, and amenities")
        df_features = df.copy()
        
        # Geospatial features (if POIs available)
        if pois:
            df_features = self.calculate_distances(df_features, pois)
            df_features = self.calculate_densities(df_features, pois)
            df_features = self.create_grid_features(df_features)
            df_features = self.create_accessibility_scores(df_features)
            df_features = self.create_interaction_features(df_features)
        
        # Temporal features
        temporal_engineer = TemporalFeatureEngineer(holidays=MAJOR_HOLIDAYS)
        df_features = temporal_engineer.add_all_temporal_features(df_features)
        
        # Review features
        review_engineer = ReviewFeatureEngineer(min_reviews=MIN_REVIEWS_FOR_TRUST)
        df_features = review_engineer.add_all_review_features(df_features)
        
        # Amenity features
        amenity_engineer = AmenityFeatureEngineer(amenity_categories=AMENITY_CATEGORIES)
        df_features = amenity_engineer.add_amenity_features(df_features)
        
        self.logger.info(f"Total features created: {len(df_features.columns)}")
        return df_features
    
    def get_feature_summary(self, df: pd.DataFrame) -> Dict[str, any]:
        """
        Get summary of created features.
        
        Args:
            df: DataFrame with features.
            
        Returns:
            Dictionary with feature summary.
        """
        # Categorize features
        distance_features = [col for col in df.columns if col.startswith('dist_nearest_')]
        density_features = [col for col in df.columns if col.startswith('count_')]
        grid_features = [col for col in df.columns if col.startswith('grid_')]
        score_features = [col for col in df.columns if col.endswith('_score')]
        interaction_features = [col for col in df.columns if 'interaction' in col or 'ratio' in col]
        
        summary = {
            'total_features': len(df.columns),
            'distance_features': len(distance_features),
            'density_features': len(density_features),
            'grid_features': len(grid_features),
            'score_features': len(score_features),
            'interaction_features': len(interaction_features),
            'feature_categories': {
                'distance': distance_features,
                'density': density_features,
                'grid': grid_features,
                'scores': score_features,
                'interactions': interaction_features
            }
        }
        
        return summary


def main():
    """
    Example usage of FeatureEngineer.
    """
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize feature engineer
    engineer = FeatureEngineer()
    
    # Example with sample data
    sample_data = pd.DataFrame({
        'latitude': [-23.5505, -22.9068, -23.5505],
        'longitude': [-46.6333, -43.1729, -46.6333],
        'price': [100, 150, 200],
        'bedrooms': [1, 2, 1],
        'bathrooms': [1, 1, 1]
    })
    
    # Create sample POI data
    sample_pois = {
        'subway': gpd.GeoDataFrame({
            'name': ['Metro Station 1', 'Metro Station 2'],
            'latitude': [-23.5505, -22.9068],
            'longitude': [-46.6333, -43.1729],
            'geometry': [Point(-46.6333, -23.5505), Point(-43.1729, -22.9068)]
        }, crs='EPSG:4326'),
        'supermarket': gpd.GeoDataFrame({
            'name': ['Supermarket 1'],
            'latitude': [-23.5505],
            'longitude': [-46.6333],
            'geometry': [Point(-46.6333, -23.5505)]
        }, crs='EPSG:4326')
    }
    
    # Create all features
    featured_data = engineer.create_all_features(sample_data, sample_pois)
    print("Featured data shape:", featured_data.shape)
    
    # Get feature summary
    summary = engineer.get_feature_summary(featured_data)
    print("Feature summary:", summary)


if __name__ == "__main__":
    main()
