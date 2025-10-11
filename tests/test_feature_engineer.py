"""
Unit tests for feature engineering module.
"""

import pytest
import pandas as pd
import numpy as np
import geopandas as gpd
from pathlib import Path
import tempfile
import shutil

from src.features.feature_engineer import FeatureEngineer


class TestFeatureEngineer:
    """Test cases for FeatureEngineer class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engineer = FeatureEngineer()
        
        # Create sample property data
        self.sample_data = pd.DataFrame({
            'latitude': [-23.5505, -22.9068, -23.5505],
            'longitude': [-46.6333, -43.1729, -46.6333],
            'price': [100, 150, 200],
            'bedrooms': [1, 2, 1],
            'bathrooms': [1, 1, 1]
        })
        
        # Create sample POI data
        self.sample_pois = {
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
    
    def test_calculate_distances(self):
        """Test distance calculation functionality."""
        result = self.engineer.calculate_distances(self.sample_data, self.sample_pois)
        
        # Check that distance columns were added
        assert 'dist_nearest_subway_km' in result.columns
        assert 'dist_nearest_supermarket_km' in result.columns
        
        # Check that distances are reasonable (not NaN for valid POIs)
        assert not result['dist_nearest_subway_km'].isna().all()
        assert not result['dist_nearest_supermarket_km'].isna().all()
        
        # Check that distances are positive
        assert (result['dist_nearest_subway_km'] >= 0).all()
        assert (result['dist_nearest_supermarket_km'] >= 0).all()
    
    def test_calculate_distances_empty_pois(self):
        """Test distance calculation with empty POI data."""
        empty_pois = {
            'subway': gpd.GeoDataFrame(columns=['name', 'geometry', 'poi_type'], crs='EPSG:4326'),
            'supermarket': gpd.GeoDataFrame(columns=['name', 'geometry', 'poi_type'], crs='EPSG:4326')
        }
        
        result = self.engineer.calculate_distances(self.sample_data, empty_pois)
        
        # Check that distance columns were added but with NaN values
        assert 'dist_nearest_subway_km' in result.columns
        assert 'dist_nearest_supermarket_km' in result.columns
        assert result['dist_nearest_subway_km'].isna().all()
        assert result['dist_nearest_supermarket_km'].isna().all()
    
    def test_calculate_densities(self):
        """Test density calculation functionality."""
        result = self.engineer.calculate_densities(self.sample_data, self.sample_pois)
        
        # Check that density columns were added
        assert 'count_subway_1km' in result.columns
        assert 'count_supermarket_1km' in result.columns
        
        # Check that densities are non-negative integers
        assert (result['count_subway_1km'] >= 0).all()
        assert (result['count_supermarket_1km'] >= 0).all()
        assert result['count_subway_1km'].dtype in ['int64', 'int32']
        assert result['count_supermarket_1km'].dtype in ['int64', 'int32']
    
    def test_calculate_densities_empty_pois(self):
        """Test density calculation with empty POI data."""
        empty_pois = {
            'subway': gpd.GeoDataFrame(columns=['name', 'geometry', 'poi_type'], crs='EPSG:4326'),
            'supermarket': gpd.GeoDataFrame(columns=['name', 'geometry', 'poi_type'], crs='EPSG:4326')
        }
        
        result = self.engineer.calculate_densities(self.sample_data, empty_pois)
        
        # Check that density columns were added with zero values
        assert 'count_subway_1km' in result.columns
        assert 'count_supermarket_1km' in result.columns
        assert (result['count_subway_1km'] == 0).all()
        assert (result['count_supermarket_1km'] == 0).all()
    
    def test_create_grid_features(self):
        """Test grid feature creation."""
        result = self.engineer.create_grid_features(self.sample_data)
        
        # Check that grid columns were added
        assert 'grid_lat' in result.columns
        assert 'grid_lon' in result.columns
        assert 'grid_id' in result.columns
        
        # Check that grid coordinates are properly rounded
        assert (result['grid_lat'] % 0.01 == 0).all()
        assert (result['grid_lon'] % 0.01 == 0).all()
        
        # Check that grid_id is unique for each grid cell
        assert result['grid_id'].nunique() <= len(result)
    
    def test_create_accessibility_scores(self):
        """Test accessibility score creation."""
        # First add distance features
        df_with_distances = self.engineer.calculate_distances(self.sample_data, self.sample_pois)
        result = self.engineer.create_accessibility_scores(df_with_distances)
        
        # Check that score columns were added
        assert 'accessibility_score' in result.columns
        assert 'transport_score' in result.columns
        
        # Check that scores are positive
        assert (result['accessibility_score'] > 0).all()
        assert (result['transport_score'] >= 0).all()
    
    def test_create_interaction_features(self):
        """Test interaction feature creation."""
        # First add basic features
        df_with_basic = self.sample_data.copy()
        df_with_basic['price_per_bedroom'] = df_with_basic['price'] / (df_with_basic['bedrooms'] + 1)
        df_with_basic['accessibility_score'] = 0.5
        
        result = self.engineer.create_interaction_features(df_with_basic)
        
        # Check that interaction features were added
        assert 'price_per_bedroom_accessibility' in result.columns
        assert 'bedroom_bathroom_ratio' in result.columns
    
    def test_create_all_features(self):
        """Test comprehensive feature creation."""
        result = self.engineer.create_all_features(self.sample_data, self.sample_pois)
        
        # Check that all expected feature types were added
        distance_features = [col for col in result.columns if col.startswith('dist_nearest_')]
        density_features = [col for col in result.columns if col.startswith('count_')]
        grid_features = [col for col in result.columns if col.startswith('grid_')]
        score_features = [col for col in result.columns if col.endswith('_score')]
        
        assert len(distance_features) > 0
        assert len(density_features) > 0
        assert len(grid_features) > 0
        assert len(score_features) > 0
        
        # Check that original data is preserved
        assert 'latitude' in result.columns
        assert 'longitude' in result.columns
        assert 'price' in result.columns
    
    def test_get_feature_summary(self):
        """Test feature summary generation."""
        # Create features first
        df_with_features = self.engineer.create_all_features(self.sample_data, self.sample_pois)
        summary = self.engineer.get_feature_summary(df_with_features)
        
        # Check summary structure
        assert 'total_features' in summary
        assert 'distance_features' in summary
        assert 'density_features' in summary
        assert 'grid_features' in summary
        assert 'score_features' in summary
        assert 'interaction_features' in summary
        assert 'feature_categories' in summary
        
        # Check that counts are reasonable
        assert summary['total_features'] > len(self.sample_data.columns)
        assert summary['distance_features'] > 0
        assert summary['density_features'] > 0
    
    def test_feature_engineer_initialization(self):
        """Test FeatureEngineer initialization."""
        assert self.engineer.grid_size == 0.01
        assert self.engineer.density_radius_km == 1.0
        assert self.engineer.distance_threshold_km == 10.0
        assert self.engineer.logger is not None
    
    def test_feature_engineer_custom_parameters(self):
        """Test FeatureEngineer with custom parameters."""
        custom_engineer = FeatureEngineer(
            grid_size=0.005,
            density_radius_km=0.5,
            distance_threshold_km=5.0
        )
        
        assert custom_engineer.grid_size == 0.005
        assert custom_engineer.density_radius_km == 0.5
        assert custom_engineer.distance_threshold_km == 5.0
    
    def test_distance_calculation_edge_cases(self):
        """Test distance calculation with edge cases."""
        # Test with single POI
        single_poi = {
            'subway': gpd.GeoDataFrame({
                'name': ['Single Station'],
                'latitude': [-23.5505],
                'longitude': [-46.6333],
                'geometry': [Point(-46.6333, -23.5505)]
            }, crs='EPSG:4326')
        }
        
        result = self.engineer.calculate_distances(self.sample_data, single_poi)
        
        # Check that distances are calculated correctly
        assert 'dist_nearest_subway_km' in result.columns
        assert not result['dist_nearest_subway_km'].isna().all()
        
        # Check that distances are reasonable (should be small for nearby points)
        nearby_distances = result[result['latitude'] == -23.5505]['dist_nearest_subway_km']
        assert nearby_distances.iloc[0] < 1.0  # Should be very close to the POI


if __name__ == "__main__":
    pytest.main([__file__])


