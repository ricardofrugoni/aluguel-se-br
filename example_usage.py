"""
Example usage of the rental price prediction system.
Demonstrates how to use individual components and the full pipeline.
"""

import logging
import pandas as pd
import numpy as np
from pathlib import Path

# Import project modules
from src.data.data_loader import DataLoader
from src.data.data_processor import DataProcessor
from src.features.poi_extractor import POIExtractor
from src.features.feature_engineer import FeatureEngineer
from src.models.baseline_models import BaselineModels
from src.models.advanced_models import AdvancedModels
from src.models.ensemble_model import EnsembleModel
from src.models.evaluation import ModelEvaluator
from src.visualization.map_visualizer import MapVisualizer
from src.visualization.data_visualizer import DataVisualizer

# Set up logging
logging.basicConfig(level=logging.INFO)


def example_data_loading():
    """Example of data loading functionality."""
    print("=== Data Loading Example ===")
    
    # Initialize data loader
    loader = DataLoader()
    
    # Load data for São Paulo
    try:
        df = loader.load_raw_data('sao_paulo')
        print(f"Loaded {len(df)} records for São Paulo")
        print(f"Columns: {list(df.columns)}")
        
        # Validate data
        validation_results = loader.validate_data(df)
        print(f"Validation results: {validation_results['total_records']} records")
        
        # Get data summary
        summary = loader.get_data_summary(df)
        print(f"Data summary: {summary['shape']}")
        
    except FileNotFoundError:
        print("Data file not found. Please download data first.")
        print("You can download data using: loader.download_data(['sao_paulo'])")
    
    return df if 'df' in locals() else None


def example_data_processing():
    """Example of data processing functionality."""
    print("\n=== Data Processing Example ===")
    
    # Create sample data
    sample_data = pd.DataFrame({
        'latitude': [-23.5505, -22.9068, -23.5505],
        'longitude': [-46.6333, -43.1729, -46.6333],
        'price': [100, 150, 200],
        'bedrooms': [1, 2, 1],
        'bathrooms': [1, 1, 1],
        'property_type': ['Entire home/apt', 'Private room', 'Entire home/apt']
    })
    
    # Initialize data processor
    processor = DataProcessor()
    
    # Clean data
    cleaned_data = processor.clean_data(sample_data)
    print(f"Cleaned data: {len(cleaned_data)} records")
    
    # Create basic features
    featured_data = processor.create_basic_features(cleaned_data)
    print(f"Added features: {len(featured_data.columns)} columns")
    
    # Handle missing values
    processed_data = processor.handle_missing_values(featured_data)
    print(f"Final processed data: {len(processed_data)} records")
    
    return processed_data


def example_poi_extraction():
    """Example of POI extraction functionality."""
    print("\n=== POI Extraction Example ===")
    
    # Initialize POI extractor
    extractor = POIExtractor()
    
    # Extract POIs for São Paulo
    try:
        pois = extractor.extract_pois('sao_paulo')
        print(f"Extracted POIs for São Paulo:")
        for poi_type, poi_gdf in pois.items():
            print(f"  {poi_type}: {len(poi_gdf)} POIs")
        
        # Get POI summary
        summary = extractor.get_poi_summary('sao_paulo', pois)
        print(f"Total POIs: {summary['total_pois']}")
        
    except Exception as e:
        print(f"POI extraction failed: {e}")
        print("This might be due to network issues or OSMnx configuration.")
    
    return pois if 'pois' in locals() else {}


def example_feature_engineering():
    """Example of feature engineering functionality."""
    print("\n=== Feature Engineering Example ===")
    
    # Create sample data
    sample_data = pd.DataFrame({
        'latitude': [-23.5505, -22.9068, -23.5505],
        'longitude': [-46.6333, -43.1729, -46.6333],
        'price': [100, 150, 200],
        'bedrooms': [1, 2, 1],
        'bathrooms': [1, 1, 1]
    })
    
    # Create sample POI data
    import geopandas as gpd
    from shapely.geometry import Point
    
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
    
    # Initialize feature engineer
    engineer = FeatureEngineer()
    
    # Create all features
    featured_data = engineer.create_all_features(sample_data, sample_pois)
    print(f"Created features: {len(featured_data.columns)} columns")
    
    # Get feature summary
    summary = engineer.get_feature_summary(featured_data)
    print(f"Feature summary: {summary['total_features']} features")
    print(f"Distance features: {summary['distance_features']}")
    print(f"Density features: {summary['density_features']}")
    print(f"Grid features: {summary['grid_features']}")
    
    return featured_data


def example_model_training():
    """Example of model training functionality."""
    print("\n=== Model Training Example ===")
    
    # Create sample data
    np.random.seed(42)
    n_samples = 1000
    n_features = 10
    
    X_train = pd.DataFrame(np.random.randn(n_samples, n_features))
    y_train = pd.Series(np.random.randn(n_samples))
    X_test = pd.DataFrame(np.random.randn(200, n_features))
    y_test = pd.Series(np.random.randn(200))
    
    # Train baseline models
    print("Training baseline models...")
    baseline = BaselineModels()
    baseline_metrics = baseline.train_all_baseline_models(X_train, y_train, X_test, y_test)
    
    for model_name, metrics in baseline_metrics.items():
        if 'error' not in metrics:
            print(f"  {model_name}: R² = {metrics['test_r2']:.4f}, MAE = {metrics['test_mae']:.4f}")
    
    # Train advanced models
    print("Training advanced models...")
    advanced = AdvancedModels()
    advanced_metrics = advanced.train_all_advanced_models(X_train, y_train, X_test, y_test)
    
    for model_name, metrics in advanced_metrics.items():
        if 'error' not in metrics:
            print(f"  {model_name}: R² = {metrics['test_r2']:.4f}, MAE = {metrics['test_mae']:.4f}")
    
    # Create ensemble
    print("Creating ensemble model...")
    ensemble = EnsembleModel()
    ensemble_metrics = ensemble.train_ensemble(X_train, y_train, X_test, y_test, 
                                             {**baseline.trained_models, **advanced.trained_models})
    print(f"  Ensemble: R² = {ensemble_metrics['test_r2']:.4f}, MAE = {ensemble_metrics['test_mae']:.4f}")
    
    return {
        'baseline': baseline_metrics,
        'advanced': advanced_metrics,
        'ensemble': ensemble_metrics
    }


def example_model_evaluation():
    """Example of model evaluation functionality."""
    print("\n=== Model Evaluation Example ===")
    
    # Create sample data
    np.random.seed(42)
    n_samples = 1000
    n_features = 10
    
    X_train = pd.DataFrame(np.random.randn(n_samples, n_features))
    y_train = pd.Series(np.random.randn(n_samples))
    X_test = pd.DataFrame(np.random.randn(200, n_features))
    y_test = pd.Series(np.random.randn(200))
    
    # Train a simple model
    from sklearn.linear_model import LinearRegression
    model = LinearRegression().fit(X_train, y_train)
    
    # Initialize evaluator
    evaluator = ModelEvaluator()
    
    # Evaluate model
    evaluation = evaluator.evaluate_model(model, X_train, y_train, X_test, y_test, 'linear_regression')
    print(f"Model evaluation results:")
    print(f"  Test R²: {evaluation['test_metrics']['r2']:.4f}")
    print(f"  Test MAE: {evaluation['test_metrics']['mae']:.4f}")
    print(f"  Test RMSE: {evaluation['test_metrics']['rmse']:.4f}")
    
    # Cross-validation
    cv_results = evaluator.cross_validate_model(model, X_train, y_train)
    print(f"  Cross-validation MAE: {cv_results['cv_mean']:.4f} (+/- {cv_results['cv_std'] * 2:.4f})")
    
    return evaluation


def example_visualization():
    """Example of visualization functionality."""
    print("\n=== Visualization Example ===")
    
    # Create sample data
    sample_data = pd.DataFrame({
        'latitude': [-23.5505, -22.9068, -23.5505, -23.5000, -22.9000],
        'longitude': [-46.6333, -43.1729, -46.6333, -46.6000, -43.1500],
        'price': [100, 150, 200, 120, 180],
        'bedrooms': [1, 2, 1, 1, 2],
        'bathrooms': [1, 1, 1, 1, 1]
    })
    
    # Create data visualizations
    print("Creating data visualizations...")
    visualizer = DataVisualizer()
    
    # Price distribution plot
    fig1 = visualizer.plot_price_distribution(sample_data)
    print("  Created price distribution plot")
    
    # Feature distributions
    fig2 = visualizer.plot_feature_distributions(sample_data)
    print("  Created feature distribution plots")
    
    # Save plots
    plot1_path = visualizer.save_plot(fig1, 'example_price_distribution.png')
    plot2_path = visualizer.save_plot(fig2, 'example_feature_distributions.png')
    print(f"  Saved plots: {plot1_path}, {plot2_path}")
    
    # Create maps
    print("Creating maps...")
    map_visualizer = MapVisualizer()
    
    # Property map
    property_map = map_visualizer.create_property_map(sample_data)
    map_path = map_visualizer.save_map(property_map, 'example_property_map.html')
    print(f"  Saved property map: {map_path}")
    
    return {
        'plots': [plot1_path, plot2_path],
        'maps': [map_path]
    }


def example_full_pipeline():
    """Example of running the full pipeline."""
    print("\n=== Full Pipeline Example ===")
    
    # This would run the complete pipeline
    # For demonstration, we'll show the structure
    
    print("To run the full pipeline, use:")
    print("  python main.py")
    print("  python main.py --cities sao_paulo rio_de_janeiro")
    print("  python main.py --no-download --no-pois")
    
    print("\nThe full pipeline includes:")
    print("  1. Data loading and validation")
    print("  2. Data cleaning and preprocessing")
    print("  3. POI extraction from OpenStreetMap")
    print("  4. Feature engineering (distances, densities, grid features)")
    print("  5. Model training (baseline, advanced, ensemble)")
    print("  6. Model evaluation and comparison")
    print("  7. Visualization creation (maps and plots)")
    print("  8. Report generation")


def main():
    """Run all examples."""
    print("Rental Price Prediction System - Example Usage")
    print("=" * 50)
    
    # Run examples
    example_data_loading()
    example_data_processing()
    example_poi_extraction()
    example_feature_engineering()
    example_model_training()
    example_model_evaluation()
    example_visualization()
    example_full_pipeline()
    
    print("\n" + "=" * 50)
    print("All examples completed!")
    print("\nFor more information, see:")
    print("  - README.md for project overview")
    print("  - config.py for configuration options")
    print("  - tests/ for unit tests")
    print("  - notebooks/ for analysis notebooks")


if __name__ == "__main__":
    main()
