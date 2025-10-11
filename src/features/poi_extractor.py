"""
POI (Points of Interest) extraction module using OpenStreetMap data.
Extracts subway stations, supermarkets, schools, hospitals, and malls.
"""

import logging
import pandas as pd
import numpy as np
import osmnx as ox
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import geopandas as gpd
from shapely.geometry import Point
import json

from config import EXTERNAL_DATA_DIR, POI_TYPES


class POIExtractor:
    """
    Extracts Points of Interest (POIs) from OpenStreetMap for Brazilian cities.
    
    Attributes:
        logger: Logger instance for tracking operations
        external_dir: Path to external data directory
        poi_data: Dictionary storing extracted POI data
    """
    
    def __init__(self, external_dir: Optional[Path] = None):
        """
        Initialize POIExtractor.
        
        Args:
            external_dir: Path to external data directory. If None, uses config default.
        """
        self.logger = logging.getLogger(__name__)
        self.external_dir = external_dir or EXTERNAL_DATA_DIR
        self.external_dir.mkdir(parents=True, exist_ok=True)
        
        self.poi_data = {}
        
        # Configure OSMnx
        ox.config(use_cache=True, log_console=False)
    
    def get_city_bounds(self, city: str) -> Tuple[float, float, float, float]:
        """
        Get bounding box for a Brazilian city.
        
        Args:
            city: City name ('sao_paulo' or 'rio_de_janeiro').
            
        Returns:
            Tuple of (north, south, east, west) coordinates.
            
        Raises:
            ValueError: If city is not supported.
        """
        city_bounds = {
            'sao_paulo': (-23.365, -23.822, -46.365, -46.822),
            'rio_de_janeiro': (-22.765, -23.065, -43.065, -43.465)
        }
        
        if city not in city_bounds:
            raise ValueError(f"City '{city}' not supported. Available: {list(city_bounds.keys())}")
        
        return city_bounds[city]
    
    def extract_pois(self, city: str, poi_types: Optional[Dict[str, Dict]] = None) -> Dict[str, gpd.GeoDataFrame]:
        """
        Extract POIs for a specific city.
        
        Args:
            city: City name to extract POIs for.
            poi_types: Dictionary of POI types to extract. If None, uses config default.
            
        Returns:
            Dictionary mapping POI type names to GeoDataFrames.
        """
        if poi_types is None:
            poi_types = POI_TYPES
        
        self.logger.info(f"Extracting POIs for {city}")
        
        # Get city bounds
        north, south, east, west = self.get_city_bounds(city)
        
        extracted_pois = {}
        
        for poi_name, poi_tags in poi_types.items():
            self.logger.info(f"Extracting {poi_name} POIs")
            
            try:
                # Extract POIs using OSMnx
                gdf = ox.geometries_from_bbox(
                    north, south, east, west,
                    tags=poi_tags
                )
                
                if len(gdf) > 0:
                    # Clean and standardize the data
                    gdf = self._clean_poi_data(gdf, poi_name)
                    extracted_pois[poi_name] = gdf
                    self.logger.info(f"Extracted {len(gdf)} {poi_name} POIs")
                else:
                    self.logger.warning(f"No {poi_name} POIs found for {city}")
                    # Create empty GeoDataFrame with proper structure
                    extracted_pois[poi_name] = gpd.GeoDataFrame(
                        columns=['name', 'geometry', 'poi_type'],
                        crs='EPSG:4326'
                    )
                
            except Exception as e:
                self.logger.error(f"Failed to extract {poi_name} POIs: {e}")
                # Create empty GeoDataFrame on error
                extracted_pois[poi_name] = gpd.GeoDataFrame(
                    columns=['name', 'geometry', 'poi_type'],
                    crs='EPSG:4326'
                )
        
        # Store in instance variable
        self.poi_data[city] = extracted_pois
        
        return extracted_pois
    
    def _clean_poi_data(self, gdf: gpd.GeoDataFrame, poi_type: str) -> gpd.GeoDataFrame:
        """
        Clean and standardize POI data.
        
        Args:
            gdf: Raw GeoDataFrame from OSMnx.
            poi_type: Type of POI for standardization.
            
        Returns:
            Cleaned GeoDataFrame.
        """
        # Create a copy to avoid modifying original
        cleaned_gdf = gdf.copy()
        
        # Ensure we have a geometry column
        if 'geometry' not in cleaned_gdf.columns:
            self.logger.warning(f"No geometry column found for {poi_type}")
            return gpd.GeoDataFrame(columns=['name', 'geometry', 'poi_type'], crs='EPSG:4326')
        
        # Filter out invalid geometries
        valid_geom = cleaned_gdf.geometry.notna() & cleaned_gdf.geometry.is_valid
        cleaned_gdf = cleaned_gdf[valid_geom]
        
        # Extract point coordinates for point geometries
        if cleaned_gdf.geometry.geom_type.iloc[0] == 'Point':
            cleaned_gdf['longitude'] = cleaned_gdf.geometry.x
            cleaned_gdf['latitude'] = cleaned_gdf.geometry.y
        else:
            # For non-point geometries, get centroid
            cleaned_gdf['longitude'] = cleaned_gdf.geometry.centroid.x
            cleaned_gdf['latitude'] = cleaned_gdf.geometry.centroid.y
        
        # Standardize name column
        if 'name' in cleaned_gdf.columns:
            cleaned_gdf['name'] = cleaned_gdf['name'].fillna('Unknown')
        else:
            cleaned_gdf['name'] = 'Unknown'
        
        # Add POI type
        cleaned_gdf['poi_type'] = poi_type
        
        # Select only necessary columns
        columns_to_keep = ['name', 'geometry', 'poi_type', 'latitude', 'longitude']
        available_columns = [col for col in columns_to_keep if col in cleaned_gdf.columns]
        cleaned_gdf = cleaned_gdf[available_columns]
        
        return cleaned_gdf
    
    def save_pois(self, city: str, pois: Optional[Dict[str, gpd.GeoDataFrame]] = None) -> Dict[str, Path]:
        """
        Save extracted POIs to files.
        
        Args:
            city: City name.
            pois: Dictionary of POI data. If None, uses stored data.
            
        Returns:
            Dictionary mapping POI types to file paths.
        """
        if pois is None:
            pois = self.poi_data.get(city, {})
        
        if not pois:
            self.logger.warning(f"No POI data found for {city}")
            return {}
        
        saved_files = {}
        
        for poi_type, gdf in pois.items():
            if len(gdf) > 0:
                # Save as GeoJSON
                filename = f"{city}_{poi_type}_pois.geojson"
                filepath = self.external_dir / filename
                
                gdf.to_file(filepath, driver='GeoJSON')
                saved_files[poi_type] = filepath
                
                self.logger.info(f"Saved {len(gdf)} {poi_type} POIs to {filepath}")
            else:
                self.logger.warning(f"No {poi_type} POIs to save for {city}")
        
        return saved_files
    
    def load_pois(self, city: str) -> Dict[str, gpd.GeoDataFrame]:
        """
        Load previously saved POI data.
        
        Args:
            city: City name.
            
        Returns:
            Dictionary mapping POI types to GeoDataFrames.
        """
        loaded_pois = {}
        
        for poi_type in POI_TYPES.keys():
            filename = f"{city}_{poi_type}_pois.geojson"
            filepath = self.external_dir / filename
            
            if filepath.exists():
                try:
                    gdf = gpd.read_file(filepath)
                    loaded_pois[poi_type] = gdf
                    self.logger.info(f"Loaded {len(gdf)} {poi_type} POIs from {filepath}")
                except Exception as e:
                    self.logger.error(f"Failed to load {poi_type} POIs: {e}")
                    # Create empty GeoDataFrame on error
                    loaded_pois[poi_type] = gpd.GeoDataFrame(
                        columns=['name', 'geometry', 'poi_type'],
                        crs='EPSG:4326'
                    )
            else:
                self.logger.warning(f"POI file not found: {filepath}")
                # Create empty GeoDataFrame
                loaded_pois[poi_type] = gpd.GeoDataFrame(
                    columns=['name', 'geometry', 'poi_type'],
                    crs='EPSG:4326'
                )
        
        return loaded_pois
    
    def get_poi_summary(self, city: str, pois: Optional[Dict[str, gpd.GeoDataFrame]] = None) -> Dict[str, any]:
        """
        Get summary statistics for extracted POIs.
        
        Args:
            city: City name.
            pois: Dictionary of POI data. If None, uses stored data.
            
        Returns:
            Dictionary with summary statistics.
        """
        if pois is None:
            pois = self.poi_data.get(city, {})
        
        summary = {
            'city': city,
            'total_pois': sum(len(gdf) for gdf in pois.values()),
            'poi_counts': {poi_type: len(gdf) for poi_type, gdf in pois.items()},
            'poi_types': list(pois.keys())
        }
        
        # Add coordinate bounds if available
        all_pois = []
        for gdf in pois.values():
            if len(gdf) > 0:
                all_pois.append(gdf)
        
        if all_pois:
            combined_gdf = pd.concat(all_pois, ignore_index=True)
            summary['bounds'] = {
                'min_lat': combined_gdf['latitude'].min(),
                'max_lat': combined_gdf['latitude'].max(),
                'min_lon': combined_gdf['longitude'].min(),
                'max_lon': combined_gdf['longitude'].max()
            }
        
        return summary


def main():
    """
    Example usage of POIExtractor.
    """
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize POI extractor
    extractor = POIExtractor()
    
    # Extract POIs for São Paulo
    try:
        pois = extractor.extract_pois('sao_paulo')
        print("Extracted POIs:", {poi_type: len(gdf) for poi_type, gdf in pois.items()})
        
        # Save POIs
        saved_files = extractor.save_pois('sao_paulo', pois)
        print("Saved files:", saved_files)
        
        # Get summary
        summary = extractor.get_poi_summary('sao_paulo', pois)
        print("POI summary:", summary)
        
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()


