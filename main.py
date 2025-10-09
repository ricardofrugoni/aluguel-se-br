"""
Main pipeline for rental price prediction project.
Orchestrates the entire machine learning workflow.
"""

import logging
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import argparse
import json
from datetime import datetime

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

from config import (
    PROJECT_ROOT, DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR, REPORTS_DIR,
    RANDOM_STATE, TEST_SIZE, CV_FOLDS
)


class RentalPricePipeline:
    """
    Main pipeline for rental price prediction.
    
    Attributes:
        logger: Logger instance for tracking operations
        data_loader: DataLoader instance
        data_processor: DataProcessor instance
        poi_extractor: POIExtractor instance
        feature_engineer: FeatureEngineer instance
        baseline_models: BaselineModels instance
        advanced_models: AdvancedModels instance
        ensemble_model: EnsembleModel instance
        evaluator: ModelEvaluator instance
        map_visualizer: MapVisualizer instance
        data_visualizer: DataVisualizer instance
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize RentalPricePipeline.
        
        Args:
            config: Configuration dictionary. If None, uses default config.
        """
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        
        # Initialize components
        self.data_loader = DataLoader()
        self.data_processor = DataProcessor()
        self.poi_extractor = POIExtractor()
        self.feature_engineer = FeatureEngineer()
        self.baseline_models = BaselineModels()
        self.advanced_models = AdvancedModels()
        self.ensemble_model = EnsembleModel()
        self.evaluator = ModelEvaluator(cv_folds=CV_FOLDS, random_state=RANDOM_STATE)
        self.map_visualizer = MapVisualizer()
        self.data_visualizer = DataVisualizer()
        
        # Pipeline state
        self.raw_data = None
        self.processed_data = None
        self.pois = {}
        self.featured_data = None
        self.trained_models = {}
        self.evaluation_results = {}
        self.predictions = None
    
    def run_full_pipeline(self, cities: List[str] = None, 
                         download_data: bool = True,
                         extract_pois: bool = True,
                         train_models: bool = True,
                         create_visualizations: bool = True) -> Dict[str, Any]:
        """
        Run the complete machine learning pipeline.
        
        Args:
            cities: List of cities to process. If None, uses default cities.
            download_data: Whether to download data.
            extract_pois: Whether to extract POIs.
            train_models: Whether to train models.
            create_visualizations: Whether to create visualizations.
            
        Returns:
            Dictionary with pipeline results.
        """
        self.logger.info("Starting full rental price prediction pipeline")
        
        if cities is None:
            cities = ['sao_paulo', 'rio_de_janeiro']
        
        pipeline_results = {
            'start_time': datetime.now().isoformat(),
            'cities': cities,
            'steps_completed': [],
            'errors': []
        }
        
        try:
            # Step 1: Data Loading
            if download_data:
                self.logger.info("Step 1: Loading data")
                self._load_data(cities)
                pipeline_results['steps_completed'].append('data_loading')
            
            # Step 2: Data Processing
            self.logger.info("Step 2: Processing data")
            self._process_data()
            pipeline_results['steps_completed'].append('data_processing')
            
            # Step 3: POI Extraction
            if extract_pois:
                self.logger.info("Step 3: Extracting POIs")
                self._extract_pois(cities)
                pipeline_results['steps_completed'].append('poi_extraction')
            
            # Step 4: Feature Engineering
            self.logger.info("Step 4: Engineering features")
            self._engineer_features()
            pipeline_results['steps_completed'].append('feature_engineering')
            
            # Step 5: Model Training
            if train_models:
                self.logger.info("Step 5: Training models")
                self._train_models()
                pipeline_results['steps_completed'].append('model_training')
            
            # Step 6: Model Evaluation
            if train_models:
                self.logger.info("Step 6: Evaluating models")
                self._evaluate_models()
                pipeline_results['steps_completed'].append('model_evaluation')
            
            # Step 7: Visualization
            if create_visualizations:
                self.logger.info("Step 7: Creating visualizations")
                self._create_visualizations()
                pipeline_results['steps_completed'].append('visualization')
            
            # Step 8: Generate Report
            self.logger.info("Step 8: Generating final report")
            self._generate_final_report()
            pipeline_results['steps_completed'].append('report_generation')
            
        except Exception as e:
            self.logger.error(f"Pipeline error: {e}")
            pipeline_results['errors'].append(str(e))
            raise
        
        pipeline_results['end_time'] = datetime.now().isoformat()
        pipeline_results['success'] = len(pipeline_results['errors']) == 0
        
        self.logger.info("Pipeline completed successfully")
        return pipeline_results
    
    def _load_data(self, cities: List[str]) -> None:
        """Load raw data for specified cities."""
        self.logger.info(f"Loading data for cities: {cities}")
        
        # Download data
        downloaded_files = self.data_loader.download_data(cities)
        self.logger.info(f"Downloaded files: {list(downloaded_files.keys())}")
        
        # Load and combine data
        self.raw_data = self.data_loader.load_multiple_cities(cities)
        self.logger.info(f"Loaded {len(self.raw_data)} records")
        
        # Validate data
        validation_results = self.data_loader.validate_data(self.raw_data)
        self.logger.info(f"Data validation: {validation_results['total_records']} records")
        
        # Get data summary
        summary = self.data_loader.get_data_summary(self.raw_data)
        self.logger.info(f"Data summary: {summary['shape']}")
    
    def _process_data(self) -> None:
        """Process and clean raw data."""
        self.logger.info("Processing raw data")
        
        # Clean data
        self.processed_data = self.data_processor.clean_data(self.raw_data)
        self.logger.info(f"Cleaned data: {len(self.processed_data)} records")
        
        # Create basic features
        self.processed_data = self.data_processor.create_basic_features(self.processed_data)
        self.logger.info(f"Added basic features: {len(self.processed_data.columns)} columns")
        
        # Handle missing values
        self.processed_data = self.data_processor.handle_missing_values(self.processed_data)
        self.logger.info(f"Handled missing values: {len(self.processed_data)} records")
        
        # Save processed data
        processed_file = self.data_processor.save_processed_data(
            self.processed_data, 'processed_rental_data.csv'
        )
        self.logger.info(f"Saved processed data to {processed_file}")
    
    def _extract_pois(self, cities: List[str]) -> None:
        """Extract Points of Interest for specified cities."""
        self.logger.info(f"Extracting POIs for cities: {cities}")
        
        for city in cities:
            self.logger.info(f"Extracting POIs for {city}")
            
            # Extract POIs
            city_pois = self.poi_extractor.extract_pois(city)
            self.pois[city] = city_pois
            
            # Save POIs
            saved_files = self.poi_extractor.save_pois(city, city_pois)
            self.logger.info(f"Saved POI files: {list(saved_files.keys())}")
            
            # Get POI summary
            summary = self.poi_extractor.get_poi_summary(city, city_pois)
            self.logger.info(f"POI summary for {city}: {summary['total_pois']} total POIs")
    
    def _engineer_features(self) -> None:
        """Create geospatial features."""
        self.logger.info("Engineering geospatial features")
        
        # Combine POIs from all cities
        all_pois = {}
        for city_pois in self.pois.values():
            for poi_type, poi_gdf in city_pois.items():
                if poi_type not in all_pois:
                    all_pois[poi_type] = poi_gdf
                else:
                    all_pois[poi_type] = pd.concat([all_pois[poi_type], poi_gdf], ignore_index=True)
        
        # Create all features
        self.featured_data = self.feature_engineer.create_all_features(
            self.processed_data, all_pois
        )
        self.logger.info(f"Created features: {len(self.featured_data.columns)} columns")
        
        # Get feature summary
        feature_summary = self.feature_engineer.get_feature_summary(self.featured_data)
        self.logger.info(f"Feature summary: {feature_summary['total_features']} features")
        
        # Save featured data
        featured_file = self.data_processor.save_processed_data(
            self.featured_data, 'featured_rental_data.csv'
        )
        self.logger.info(f"Saved featured data to {featured_file}")
    
    def _train_models(self) -> None:
        """Train all machine learning models."""
        self.logger.info("Training machine learning models")
        
        # Prepare data for modeling
        X_train, y_train, X_test, y_test = self.data_processor.prepare_model_data(
            self.featured_data, test_size=TEST_SIZE, random_state=RANDOM_STATE
        )
        self.logger.info(f"Prepared data: Train {X_train.shape}, Test {X_test.shape}")
        
        # Train baseline models
        self.logger.info("Training baseline models")
        baseline_metrics = self.baseline_models.train_all_baseline_models(
            X_train, y_train, X_test, y_test
        )
        self.trained_models.update(self.baseline_models.trained_models)
        self.logger.info(f"Baseline models trained: {list(baseline_metrics.keys())}")
        
        # Train advanced models
        self.logger.info("Training advanced models")
        advanced_metrics = self.advanced_models.train_all_advanced_models(
            X_train, y_train, X_test, y_test
        )
        self.trained_models.update(self.advanced_models.trained_models)
        self.logger.info(f"Advanced models trained: {list(advanced_metrics.keys())}")
        
        # Create ensemble model
        self.logger.info("Creating ensemble model")
        ensemble_metrics = self.ensemble_model.train_ensemble(
            X_train, y_train, X_test, y_test, self.trained_models
        )
        self.trained_models['ensemble'] = self.ensemble_model.ensemble_model
        self.logger.info(f"Ensemble model created with R²: {ensemble_metrics['test_r2']:.4f}")
        
        # Store test data for evaluation
        self.X_test = X_test
        self.y_test = y_test
    
    def _evaluate_models(self) -> None:
        """Evaluate all trained models."""
        self.logger.info("Evaluating models")
        
        # Evaluate individual models
        for model_name, model in self.trained_models.items():
            if model_name == 'ensemble':
                continue
            
            evaluation = self.evaluator.evaluate_model(
                model, self.X_test, self.y_test, self.X_test, self.y_test, model_name
            )
            self.evaluation_results[model_name] = evaluation
            self.logger.info(f"Evaluated {model_name}: R² = {evaluation['test_metrics']['r2']:.4f}")
        
        # Compare all models
        comparison_df = self.evaluator.compare_models(self.trained_models, self.X_test, self.y_test)
        self.logger.info("Model comparison completed")
        
        # Create evaluation report
        report = self.evaluator.create_evaluation_report(
            self.trained_models, self.X_test, self.y_test,
            save_path=REPORTS_DIR / 'evaluation_report.json'
        )
        self.logger.info(f"Evaluation report created: {report['summary']['best_model']}")
        
        # Store evaluation results
        self.evaluation_results['comparison'] = comparison_df
        self.evaluation_results['report'] = report
    
    def _create_visualizations(self) -> None:
        """Create visualizations and maps."""
        self.logger.info("Creating visualizations")
        
        # Create data visualizations
        figures = self.data_visualizer.create_comprehensive_report(
            self.featured_data, 
            {name: results['test_metrics'] for name, results in self.evaluation_results.items() 
             if 'test_metrics' in results},
            pd.DataFrame(),  # Feature importance would go here
            self.y_test,
            self.trained_models['ensemble'].predict(self.X_test),
            'Ensemble Model'
        )
        
        # Save plots
        for i, fig in enumerate(figures):
            plot_file = self.data_visualizer.save_plot(fig, f'analysis_plot_{i+1}.png')
            self.logger.info(f"Saved plot: {plot_file}")
        
        # Create maps
        self.logger.info("Creating maps")
        
        # Property map
        property_map = self.map_visualizer.create_property_map(self.featured_data)
        property_map_file = self.map_visualizer.save_map(property_map, 'property_map.html')
        self.logger.info(f"Saved property map: {property_map_file}")
        
        # POI map
        all_pois = {}
        for city_pois in self.pois.values():
            for poi_type, poi_gdf in city_pois.items():
                if poi_type not in all_pois:
                    all_pois[poi_type] = poi_gdf
                else:
                    all_pois[poi_type] = pd.concat([all_pois[poi_type], poi_gdf], ignore_index=True)
        
        poi_map = self.map_visualizer.create_poi_map(all_pois)
        poi_map_file = self.map_visualizer.save_map(poi_map, 'poi_map.html')
        self.logger.info(f"Saved POI map: {poi_map_file}")
        
        # Combined map
        combined_map = self.map_visualizer.create_combined_map(
            self.featured_data, all_pois
        )
        combined_map_file = self.map_visualizer.save_map(combined_map, 'combined_map.html')
        self.logger.info(f"Saved combined map: {combined_map_file}")
    
    def _generate_final_report(self) -> None:
        """Generate final project report."""
        self.logger.info("Generating final report")
        
        # Create comprehensive report
        report = {
            'project_info': {
                'name': 'Rental Price Prediction for Southeast Brazil',
                'description': 'Machine learning system for predicting rental prices',
                'created_at': datetime.now().isoformat(),
                'version': '1.0.0'
            },
            'data_summary': {
                'total_records': len(self.featured_data),
                'total_features': len(self.featured_data.columns),
                'cities': list(self.pois.keys()),
                'poi_counts': {city: sum(len(poi_gdf) for poi_gdf in city_pois.values()) 
                              for city, city_pois in self.pois.items()}
            },
            'model_performance': {
                name: results.get('test_metrics', {}) 
                for name, results in self.evaluation_results.items()
                if 'test_metrics' in results
            },
            'best_model': self.evaluation_results.get('report', {}).get('summary', {}).get('best_model', 'Unknown'),
            'recommendations': self.evaluation_results.get('report', {}).get('recommendations', [])
        }
        
        # Save report
        report_file = REPORTS_DIR / 'final_report.json'
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        self.logger.info(f"Final report saved to {report_file}")
    
    def predict_prices(self, new_data: pd.DataFrame) -> pd.Series:
        """
        Predict rental prices for new data.
        
        Args:
            new_data: DataFrame with property features.
            
        Returns:
            Series with price predictions.
        """
        if 'ensemble' not in self.trained_models:
            raise ValueError("Ensemble model not trained. Run pipeline first.")
        
        # Make predictions using ensemble model
        predictions = self.trained_models['ensemble'].predict(new_data)
        return pd.Series(predictions, name='predicted_price')


def main():
    """Main function to run the pipeline."""
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Rental Price Prediction Pipeline')
    parser.add_argument('--cities', nargs='+', default=['sao_paulo', 'rio_de_janeiro'],
                       help='Cities to process')
    parser.add_argument('--no-download', action='store_true',
                       help='Skip data download')
    parser.add_argument('--no-pois', action='store_true',
                       help='Skip POI extraction')
    parser.add_argument('--no-train', action='store_true',
                       help='Skip model training')
    parser.add_argument('--no-viz', action='store_true',
                       help='Skip visualization creation')
    parser.add_argument('--config', type=str,
                       help='Path to configuration file')
    
    args = parser.parse_args()
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(PROJECT_ROOT / 'logs' / 'pipeline.log'),
            logging.StreamHandler()
        ]
    )
    
    # Load configuration if provided
    config = {}
    if args.config:
        with open(args.config, 'r') as f:
            config = json.load(f)
    
    # Initialize and run pipeline
    pipeline = RentalPricePipeline(config)
    
    try:
        results = pipeline.run_full_pipeline(
            cities=args.cities,
            download_data=not args.no_download,
            extract_pois=not args.no_pois,
            train_models=not args.no_train,
            create_visualizations=not args.no_viz
        )
        
        print(f"Pipeline completed successfully!")
        print(f"Steps completed: {results['steps_completed']}")
        print(f"Best model: {results.get('best_model', 'Unknown')}")
        
    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        raise


if __name__ == "__main__":
    main()
