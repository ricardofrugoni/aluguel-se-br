"""
Example script to run the rental price prediction pipeline.
This script demonstrates how to use the system with different configurations.
"""

import logging
import json
from pathlib import Path
from main import RentalPricePipeline

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_basic_example():
    """Run a basic example with default settings."""
    print("=== Basic Pipeline Example ===")
    
    # Initialize pipeline
    pipeline = RentalPricePipeline()
    
    # Run pipeline with default settings
    results = pipeline.run_full_pipeline(
        cities=['sao_paulo', 'rio_de_janeiro'],
        download_data=True,
        extract_pois=True,
        train_models=True,
        create_visualizations=True
    )
    
    print(f"Pipeline completed: {results['success']}")
    print(f"Steps completed: {results['steps_completed']}")
    if results['errors']:
        print(f"Errors: {results['errors']}")


def run_custom_config_example():
    """Run pipeline with custom configuration."""
    print("\n=== Custom Configuration Example ===")
    
    # Load custom configuration
    config_file = Path("config_example.json")
    if config_file.exists():
        with open(config_file, 'r') as f:
            config = json.load(f)
    else:
        config = {}
    
    # Initialize pipeline with custom config
    pipeline = RentalPricePipeline(config)
    
    # Run pipeline with custom settings
    results = pipeline.run_full_pipeline(
        cities=['sao_paulo'],
        download_data=False,  # Use existing data
        extract_pois=True,
        train_models=True,
        create_visualizations=True
    )
    
    print(f"Pipeline completed: {results['success']}")
    print(f"Steps completed: {results['steps_completed']}")


def run_prediction_example():
    """Run prediction example with trained models."""
    print("\n=== Prediction Example ===")
    
    # Initialize pipeline
    pipeline = RentalPricePipeline()
    
    # Create sample new data
    import pandas as pd
    import numpy as np
    
    new_data = pd.DataFrame({
        'latitude': [-23.5505, -22.9068, -23.5000],
        'longitude': [-46.6333, -43.1729, -46.6000],
        'bedrooms': [1, 2, 1],
        'bathrooms': [1, 1, 1],
        'property_type': ['Entire home/apt', 'Private room', 'Entire home/apt']
    })
    
    try:
        # Make predictions (requires trained models)
        predictions = pipeline.predict_prices(new_data)
        print(f"Predictions: {predictions.tolist()}")
    except ValueError as e:
        print(f"Prediction failed: {e}")
        print("Please train models first by running the full pipeline.")


def run_individual_components_example():
    """Run individual components example."""
    print("\n=== Individual Components Example ===")
    
    # Import individual components
    from src.data.data_loader import DataLoader
    from src.data.data_processor import DataProcessor
    from src.features.poi_extractor import POIExtractor
    from src.features.feature_engineer import FeatureEngineer
    
    # Initialize components
    loader = DataLoader()
    processor = DataProcessor()
    extractor = POIExtractor()
    engineer = FeatureEngineer()
    
    print("Components initialized successfully")
    print("  - DataLoader: For loading Airbnb data")
    print("  - DataProcessor: For cleaning and preprocessing")
    print("  - POIExtractor: For extracting Points of Interest")
    print("  - FeatureEngineer: For creating geospatial features")
    
    # Example of using individual components
    try:
        # Load data
        df = loader.load_raw_data('sao_paulo')
        print(f"  Loaded {len(df)} records")
        
        # Process data
        cleaned_df = processor.clean_data(df)
        print(f"  Cleaned data: {len(cleaned_df)} records")
        
        # Extract POIs
        pois = extractor.extract_pois('sao_paulo')
        print(f"  Extracted POIs: {sum(len(poi_gdf) for poi_gdf in pois.values())} total")
        
        # Create features
        featured_df = engineer.create_all_features(cleaned_df, pois)
        print(f"  Created features: {len(featured_df.columns)} columns")
        
    except FileNotFoundError:
        print("  Data files not found. Please download data first.")
    except Exception as e:
        print(f"  Error: {e}")


def run_testing_example():
    """Run testing example."""
    print("\n=== Testing Example ===")
    
    import subprocess
    import sys
    
    try:
        # Run tests
        result = subprocess.run([sys.executable, '-m', 'pytest', 'tests/', '-v'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("All tests passed!")
            print(result.stdout)
        else:
            print("Some tests failed:")
            print(result.stdout)
            print(result.stderr)
            
    except Exception as e:
        print(f"Testing failed: {e}")


def main():
    """Run all examples."""
    print("Rental Price Prediction System - Example Usage")
    print("=" * 60)
    
    # Run examples
    run_basic_example()
    run_custom_config_example()
    run_prediction_example()
    run_individual_components_example()
    run_testing_example()
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("\nFor more information, see:")
    print("  - README.md for project overview")
    print("  - docs/API_REFERENCE.md for detailed API documentation")
    print("  - config.py for configuration options")
    print("  - example_usage.py for more examples")


if __name__ == "__main__":
    main()
