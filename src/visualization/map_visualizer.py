"""
Map visualization module using Folium for rental price prediction.
Creates interactive maps showing properties, POIs, and predictions.
"""

import logging
import pandas as pd
import numpy as np
import folium
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import geopandas as gpd
from folium import plugins

from config import REPORTS_DIR


class MapVisualizer:
    """
    Creates interactive maps for rental price analysis.
    
    Attributes:
        logger: Logger instance for tracking operations
        reports_dir: Path to reports directory
        base_maps: Dictionary storing base map configurations
    """
    
    def __init__(self, reports_dir: Optional[Path] = None):
        """
        Initialize MapVisualizer.
        
        Args:
            reports_dir: Path to reports directory. If None, uses config default.
        """
        self.logger = logging.getLogger(__name__)
        self.reports_dir = reports_dir or REPORTS_DIR
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Base map configurations
        self.base_maps = {
            'openstreetmap': folium.TileLayer('OpenStreetMap'),
            'cartodb_positron': folium.TileLayer('CartoDB positron'),
            'cartodb_dark': folium.TileLayer('CartoDB dark_matter')
        }
    
    def create_property_map(self, df: pd.DataFrame, price_col: str = 'price',
                           lat_col: str = 'latitude', lon_col: str = 'longitude',
                           color_by: str = 'price', size_by: str = 'price',
                           title: str = 'Rental Properties Map') -> folium.Map:
        """
        Create interactive map showing rental properties.
        
        Args:
            df: DataFrame with property data.
            price_col: Name of price column.
            lat_col: Name of latitude column.
            lon_col: Name of longitude column.
            color_by: Column to use for coloring markers.
            size_by: Column to use for marker size.
            title: Title for the map.
            
        Returns:
            Folium map object.
        """
        self.logger.info(f"Creating property map with {len(df)} properties")
        
        # Calculate map center
        center_lat = df[lat_col].mean()
        center_lon = df[lon_col].mean()
        
        # Create base map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=11,
            tiles=None
        )
        
        # Add base layers
        for name, tile in self.base_maps.items():
            tile.add_to(m)
        
        # Create color scale
        if color_by in df.columns:
            color_scale = self._create_color_scale(df[color_by])
        else:
            color_scale = lambda x: 'blue'
        
        # Create size scale
        if size_by in df.columns:
            size_scale = self._create_size_scale(df[size_by])
        else:
            size_scale = lambda x: 8
        
        # Add property markers
        for idx, row in df.iterrows():
            # Create popup content
            popup_content = self._create_property_popup(row, price_col)
            
            # Create marker
            folium.CircleMarker(
                location=[row[lat_col], row[lon_col]],
                radius=size_scale(row[size_by]),
                popup=folium.Popup(popup_content, max_width=300),
                color=color_scale(row[color_by]),
                fill=True,
                fillColor=color_scale(row[color_by]),
                fillOpacity=0.7,
                weight=1
            ).add_to(m)
        
        # Add legend
        self._add_color_legend(m, df[color_by], color_scale)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        self.logger.info("Property map created successfully")
        return m
    
    def create_poi_map(self, pois: Dict[str, gpd.GeoDataFrame], 
                      title: str = 'Points of Interest Map') -> folium.Map:
        """
        Create map showing Points of Interest.
        
        Args:
            pois: Dictionary mapping POI types to GeoDataFrames.
            title: Title for the map.
            
        Returns:
            Folium map object.
        """
        self.logger.info("Creating POI map")
        
        # Calculate map center from all POIs
        all_lats = []
        all_lons = []
        for poi_gdf in pois.values():
            if len(poi_gdf) > 0:
                all_lats.extend(poi_gdf['latitude'].tolist())
                all_lons.extend(poi_gdf['longitude'].tolist())
        
        if not all_lats:
            self.logger.warning("No POI data available for map creation")
            return folium.Map(location=[-23.5505, -46.6333], zoom_start=11)
        
        center_lat = np.mean(all_lats)
        center_lon = np.mean(all_lons)
        
        # Create base map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=11,
            tiles=None
        )
        
        # Add base layers
        for name, tile in self.base_maps.items():
            tile.add_to(m)
        
        # POI colors and icons
        poi_config = {
            'subway': {'color': 'red', 'icon': 'subway'},
            'supermarket': {'color': 'green', 'icon': 'shopping-cart'},
            'school': {'color': 'blue', 'icon': 'graduation-cap'},
            'hospital': {'color': 'purple', 'icon': 'hospital'},
            'mall': {'color': 'orange', 'icon': 'shopping-bag'}
        }
        
        # Add POI markers
        for poi_type, poi_gdf in pois.items():
            if len(poi_gdf) == 0:
                continue
            
            config = poi_config.get(poi_type, {'color': 'gray', 'icon': 'map-marker'})
            
            for idx, row in poi_gdf.iterrows():
                # Create popup content
                popup_content = f"""
                <b>{poi_type.title()}</b><br>
                Name: {row.get('name', 'Unknown')}<br>
                Type: {poi_type}
                """
                
                # Create marker
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=folium.Popup(popup_content, max_width=200),
                    icon=folium.Icon(color=config['color'], icon=config['icon'])
                ).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        self.logger.info("POI map created successfully")
        return m
    
    def create_prediction_map(self, df: pd.DataFrame, predictions: pd.Series,
                             lat_col: str = 'latitude', lon_col: str = 'longitude',
                             title: str = 'Price Predictions Map') -> folium.Map:
        """
        Create map showing price predictions.
        
        Args:
            df: DataFrame with property data.
            predictions: Series with predictions.
            lat_col: Name of latitude column.
            lon_col: Name of longitude column.
            title: Title for the map.
            
        Returns:
            Folium map object.
        """
        self.logger.info("Creating prediction map")
        
        # Calculate map center
        center_lat = df[lat_col].mean()
        center_lon = df[lon_col].mean()
        
        # Create base map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=11,
            tiles=None
        )
        
        # Add base layers
        for name, tile in self.base_maps.items():
            tile.add_to(m)
        
        # Create color scale for predictions
        color_scale = self._create_color_scale(predictions)
        size_scale = self._create_size_scale(predictions)
        
        # Add prediction markers
        for idx, row in df.iterrows():
            pred_value = predictions.iloc[idx]
            
            # Create popup content
            popup_content = f"""
            <b>Price Prediction</b><br>
            Predicted Price: R$ {pred_value:,.2f}<br>
            Location: ({row[lat_col]:.4f}, {row[lon_col]:.4f})
            """
            
            # Create marker
            folium.CircleMarker(
                location=[row[lat_col], row[lon_col]],
                radius=size_scale(pred_value),
                popup=folium.Popup(popup_content, max_width=300),
                color=color_scale(pred_value),
                fill=True,
                fillColor=color_scale(pred_value),
                fillOpacity=0.7,
                weight=1
            ).add_to(m)
        
        # Add legend
        self._add_color_legend(m, predictions, color_scale)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        self.logger.info("Prediction map created successfully")
        return m
    
    def create_heatmap(self, df: pd.DataFrame, value_col: str = 'price',
                      lat_col: str = 'latitude', lon_col: str = 'longitude',
                      title: str = 'Price Heatmap') -> folium.Map:
        """
        Create heatmap showing price density.
        
        Args:
            df: DataFrame with property data.
            value_col: Column to use for heatmap values.
            lat_col: Name of latitude column.
            lon_col: Name of longitude column.
            title: Title for the map.
            
        Returns:
            Folium map object.
        """
        self.logger.info("Creating price heatmap")
        
        # Calculate map center
        center_lat = df[lat_col].mean()
        center_lon = df[lon_col].mean()
        
        # Create base map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=11,
            tiles=None
        )
        
        # Add base layers
        for name, tile in self.base_maps.items():
            tile.add_to(m)
        
        # Prepare heatmap data
        heatmap_data = [[row[lat_col], row[lon_col], row[value_col]] for idx, row in df.iterrows()]
        
        # Add heatmap layer
        plugins.HeatMap(
            heatmap_data,
            name='Price Heatmap',
            min_opacity=0.2,
            max_zoom=18,
            radius=25,
            blur=15,
            gradient={0.4: 'blue', 0.6: 'cyan', 0.7: 'lime', 0.8: 'yellow', 1.0: 'red'}
        ).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        self.logger.info("Heatmap created successfully")
        return m
    
    def create_combined_map(self, df: pd.DataFrame, pois: Dict[str, gpd.GeoDataFrame],
                          predictions: Optional[pd.Series] = None,
                          lat_col: str = 'latitude', lon_col: str = 'longitude',
                          price_col: str = 'price') -> folium.Map:
        """
        Create combined map with properties, POIs, and predictions.
        
        Args:
            df: DataFrame with property data.
            pois: Dictionary mapping POI types to GeoDataFrames.
            predictions: Series with predictions. If None, uses actual prices.
            lat_col: Name of latitude column.
            lon_col: Name of longitude column.
            price_col: Name of price column.
            
        Returns:
            Folium map object.
        """
        self.logger.info("Creating combined map")
        
        # Calculate map center
        center_lat = df[lat_col].mean()
        center_lon = df[lon_col].mean()
        
        # Create base map
        m = folium.Map(
            location=[center_lat, center_lon],
            zoom_start=11,
            tiles=None
        )
        
        # Add base layers
        for name, tile in self.base_maps.items():
            tile.add_to(m)
        
        # Add property markers
        property_layer = folium.FeatureGroup(name='Properties')
        for idx, row in df.iterrows():
            price_value = predictions.iloc[idx] if predictions is not None else row[price_col]
            
            # Create popup content
            popup_content = self._create_property_popup(row, price_col)
            if predictions is not None:
                popup_content += f"<br>Predicted Price: R$ {price_value:,.2f}"
            
            # Create marker
            folium.CircleMarker(
                location=[row[lat_col], row[lon_col]],
                radius=8,
                popup=folium.Popup(popup_content, max_width=300),
                color='blue',
                fill=True,
                fillColor='blue',
                fillOpacity=0.7,
                weight=1
            ).add_to(property_layer)
        
        property_layer.add_to(m)
        
        # Add POI markers
        poi_layer = folium.FeatureGroup(name='Points of Interest')
        poi_config = {
            'subway': {'color': 'red', 'icon': 'subway'},
            'supermarket': {'color': 'green', 'icon': 'shopping-cart'},
            'school': {'color': 'blue', 'icon': 'graduation-cap'},
            'hospital': {'color': 'purple', 'icon': 'hospital'},
            'mall': {'color': 'orange', 'icon': 'shopping-bag'}
        }
        
        for poi_type, poi_gdf in pois.items():
            if len(poi_gdf) == 0:
                continue
            
            config = poi_config.get(poi_type, {'color': 'gray', 'icon': 'map-marker'})
            
            for idx, row in poi_gdf.iterrows():
                popup_content = f"""
                <b>{poi_type.title()}</b><br>
                Name: {row.get('name', 'Unknown')}
                """
                
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=folium.Popup(popup_content, max_width=200),
                    icon=folium.Icon(color=config['color'], icon=config['icon'])
                ).add_to(poi_layer)
        
        poi_layer.add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        self.logger.info("Combined map created successfully")
        return m
    
    def save_map(self, map_obj: folium.Map, filename: str) -> Path:
        """
        Save map to HTML file.
        
        Args:
            map_obj: Folium map object to save.
            filename: Name of the file to save.
            
        Returns:
            Path to saved file.
        """
        filepath = self.reports_dir / filename
        
        map_obj.save(str(filepath))
        self.logger.info(f"Map saved to {filepath}")
        
        return filepath
    
    def _create_color_scale(self, values: pd.Series) -> callable:
        """
        Create color scale function for mapping values to colors.
        
        Args:
            values: Series with values to map.
            
        Returns:
            Function that maps values to colors.
        """
        # Define color scale
        colors = ['darkblue', 'blue', 'lightblue', 'green', 'yellow', 'orange', 'red']
        
        # Create bins
        bins = np.linspace(values.min(), values.max(), len(colors))
        
        def color_scale(value):
            for i, bin_val in enumerate(bins):
                if value <= bin_val:
                    return colors[i]
            return colors[-1]
        
        return color_scale
    
    def _create_size_scale(self, values: pd.Series, min_size: int = 5, max_size: int = 20) -> callable:
        """
        Create size scale function for mapping values to marker sizes.
        
        Args:
            values: Series with values to map.
            min_size: Minimum marker size.
            max_size: Maximum marker size.
            
        Returns:
            Function that maps values to sizes.
        """
        min_val = values.min()
        max_val = values.max()
        
        def size_scale(value):
            normalized = (value - min_val) / (max_val - min_val)
            return min_size + (max_size - min_size) * normalized
        
        return size_scale
    
    def _create_property_popup(self, row: pd.Series, price_col: str) -> str:
        """
        Create popup content for property markers.
        
        Args:
            row: Property data row.
            price_col: Name of price column.
            
        Returns:
            HTML string for popup content.
        """
        popup_content = f"""
        <b>Property Details</b><br>
        Price: R$ {row[price_col]:,.2f}<br>
        Location: ({row['latitude']:.4f}, {row['longitude']:.4f})
        """
        
        # Add additional details if available
        if 'bedrooms' in row:
            popup_content += f"<br>Bedrooms: {row['bedrooms']}"
        if 'bathrooms' in row:
            popup_content += f"<br>Bathrooms: {row['bathrooms']}"
        if 'property_type' in row:
            popup_content += f"<br>Type: {row['property_type']}"
        
        return popup_content
    
    def _add_color_legend(self, map_obj: folium.Map, values: pd.Series, color_scale: callable) -> None:
        """
        Add color legend to map.
        
        Args:
            map_obj: Folium map object.
            values: Series with values for legend.
            color_scale: Color scale function.
        """
        # Create legend HTML
        legend_html = '''
        <div style="position: fixed; 
                    bottom: 50px; left: 50px; width: 200px; height: 120px; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <p><b>Price Range</b></p>
        '''
        
        # Add color scale to legend
        bins = np.linspace(values.min(), values.max(), 5)
        for i in range(len(bins) - 1):
            color = color_scale(bins[i])
            legend_html += f'<p><i style="background:{color}"></i> {bins[i]:.0f} - {bins[i+1]:.0f}</p>'
        
        legend_html += '</div>'
        
        map_obj.get_root().html.add_child(folium.Element(legend_html))


def main():
    """
    Example usage of MapVisualizer.
    """
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize map visualizer
    visualizer = MapVisualizer()
    
    # Example with sample data
    sample_data = pd.DataFrame({
        'latitude': [-23.5505, -22.9068, -23.5505],
        'longitude': [-46.6333, -43.1729, -46.6333],
        'price': [100, 150, 200],
        'bedrooms': [1, 2, 1],
        'bathrooms': [1, 1, 1]
    })
    
    # Create property map
    property_map = visualizer.create_property_map(sample_data)
    print("Property map created")
    
    # Save map
    saved_path = visualizer.save_map(property_map, 'sample_property_map.html')
    print(f"Map saved to {saved_path}")


if __name__ == "__main__":
    main()
