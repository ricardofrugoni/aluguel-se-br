# API Reference

This document provides detailed API documentation for the rental price
prediction system.

## Data Loading Module

### DataLoader

Handles loading and basic processing of Airbnb rental data.

#### Methods

- `download_data(cities: List[str]) -> Dict[str, Path]`

  - Downloads Airbnb data for specified cities

  - Returns dictionary mapping city names to file paths

- `load_raw_data(city: str, filepath: Optional[Path] = None) -> pd.DataFrame`

  - Loads raw Airbnb data for a specific city

  - Returns DataFrame with raw data

- `load_multiple_cities(cities: List[str]) -> pd.DataFrame`

  - Loads and combines data from multiple cities

  - Returns combined DataFrame

- `validate_data(df: pd.DataFrame) -> Dict[str, Any]`

  - Performs basic data validation

  - Returns validation results dictionary

- `get_data_summary(df: pd.DataFrame) -> Dict[str, Any]`

  - Generates summary statistics for the dataset

  - Returns summary dictionary

### DataProcessor

Handles data cleaning and preprocessing.

#### Methods

- `clean_data(df: pd.DataFrame) -> pd.DataFrame`

  - Cleans raw Airbnb data

  - Returns cleaned DataFrame

- `create_basic_features(df: pd.DataFrame) -> pd.DataFrame`

  - Creates basic features from raw data

  - Returns DataFrame with basic features

- `handle_missing_values(df: pd.DataFrame, strategy: str = 'median') -> pd.DataFrame`

  - Handles missing values in the dataset

  - Returns DataFrame with missing values handled

- `prepare_model_data(df: pd.DataFrame, target_col: str = 'price', test_size: float = 0.2, random_state: int = 42) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]`

  - Prepares data for machine learning models

  - Returns train/test splits

## Feature Engineering Module

### POIExtractor

Extracts Points of Interest from OpenStreetMap.

#### Methods

- `extract_pois(city: str, poi_types: Optional[Dict[str, Dict]] = None) -> Dict[str, gpd.GeoDataFrame]`

  - Extracts POIs for a specific city

  - Returns dictionary mapping POI types to GeoDataFrames

- `save_pois(city: str, pois: Optional[Dict[str, gpd.GeoDataFrame]] = None) -> Dict[str, Path]`

  - Saves extracted POIs to files

  - Returns dictionary mapping POI types to file paths

- `load_pois(city: str) -> Dict[str, gpd.GeoDataFrame]`

  - Loads previously saved POI data

  - Returns dictionary mapping POI types to GeoDataFrames

### FeatureEngineer

Creates geospatial features for rental price prediction.

#### Methods

- `calculate_distances(df: pd.DataFrame, pois: Dict[str, gpd.GeoDataFrame]) -> pd.DataFrame`

  - Calculates distances from properties to nearest POIs

  - Returns DataFrame with distance features

- `calculate_densities(df: pd.DataFrame, pois: Dict[str, gpd.GeoDataFrame]) -> pd.DataFrame`

  - Calculates POI densities within specified radius

  - Returns DataFrame with density features

- `create_grid_features(df: pd.DataFrame) -> pd.DataFrame`

  - Creates grid-based features by aggregating data within grid cells

  - Returns DataFrame with grid features

- `create_accessibility_scores(df: pd.DataFrame) -> pd.DataFrame`

  - Creates accessibility and transport scores based on POI distances

  - Returns DataFrame with accessibility scores

- `create_all_features(df: pd.DataFrame, pois: Dict[str, gpd.GeoDataFrame]) -> pd.DataFrame`

  - Creates all geospatial features in one pipeline

  - Returns DataFrame with all features

## Machine Learning Models

### BaselineModels

Baseline machine learning models for rental price prediction.

#### Methods

- `train_ridge_regression(X_train: pd.DataFrame, y_train: pd.Series, X_test: pd.DataFrame, y_test: pd.Series, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`

  - Trains Ridge Regression model

  - Returns performance metrics

- `train_random_forest(X_train: pd.DataFrame, y_train: pd.Series, X_test: pd.DataFrame, y_test: pd.Series, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`

  - Trains Random Forest model

  - Returns performance metrics

- `train_all_baseline_models(X_train: pd.DataFrame, y_train: pd.Series, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Dict[str, Any]]`

  - Trains all baseline models

  - Returns dictionary mapping model names to performance metrics

### AdvancedModels

Advanced machine learning models for rental price prediction.

#### Methods

- `train_xgboost(X_train: pd.DataFrame, y_train: pd.Series, X_test: pd.DataFrame, y_test: pd.Series, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`

  - Trains XGBoost model

  - Returns performance metrics

- `train_lightgbm(X_train: pd.DataFrame, y_train: pd.Series, X_test: pd.DataFrame, y_test: pd.Series, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`

  - Trains LightGBM model

  - Returns performance metrics

- `train_catboost(X_train: pd.DataFrame, y_train: pd.Series, X_test: pd.DataFrame, y_test: pd.Series, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]`

  - Trains CatBoost model

  - Returns performance metrics

### EnsembleModel

Ensemble model that combines multiple machine learning models.

#### Methods

- `create_ensemble(models: Dict[str, Any], weights: Optional[Dict[str, float]] = None) -> VotingRegressor`

  - Creates ensemble model from individual models

  - Returns trained ensemble model

- `train_ensemble(X_train: pd.DataFrame, y_train: pd.Series, X_test: pd.DataFrame, y_test: pd.Series, models: Dict[str, Any], weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]`

  - Trains ensemble model and evaluates performance

  - Returns performance metrics

## Model Evaluation

### ModelEvaluator

Model evaluation and comparison utilities.

#### Methods

- `calculate_metrics(y_true: pd.Series, y_pred: pd.Series) -> Dict[str, float]`

  - Calculates comprehensive evaluation metrics

  - Returns dictionary with metrics

- `evaluate_model(model: Any, X_train: pd.DataFrame, y_train: pd.Series, X_test: pd.DataFrame, y_test: pd.Series, model_name: str = 'model') -> Dict[str, Any]`

  - Comprehensive evaluation of a model

  - Returns evaluation results

- `compare_models(models: Dict[str, Any], X_test: pd.DataFrame, y_test: pd.Series) -> pd.DataFrame`

  - Compares performance of multiple models

  - Returns comparison DataFrame

- `create_evaluation_report(models: Dict[str, Any], X_test: pd.DataFrame, y_test: pd.Series, save_path: Optional[Path] = None) -> Dict[str, Any]`

  - Creates comprehensive evaluation report

  - Returns evaluation report

## Visualization

### MapVisualizer

Creates interactive maps for rental price analysis.

#### Methods

- `create_property_map(df: pd.DataFrame, price_col: str = 'price', lat_col: str = 'latitude', lon_col: str = 'longitude', color_by: str = 'price', size_by: str = 'price', title: str = 'Rental Properties Map') -> folium.Map`

  - Creates interactive map showing rental properties

  - Returns Folium map object

- `create_poi_map(pois: Dict[str, gpd.GeoDataFrame], title: str = 'Points of Interest Map') -> folium.Map`

  - Creates map showing Points of Interest

  - Returns Folium map object

- `create_prediction_map(df: pd.DataFrame, predictions: pd.Series, lat_col: str = 'latitude', lon_col: str = 'longitude', title: str = 'Price Predictions Map') -> folium.Map`

  - Creates map showing price predictions

  - Returns Folium map object

### DataVisualizer

Creates data visualizations for rental price analysis.

#### Methods

- `plot_price_distribution(df: pd.DataFrame, price_col: str = 'price', title: str = 'Price Distribution') -> plt.Figure`

  - Creates price distribution plots

  - Returns Matplotlib figure object

- `plot_feature_distributions(df: pd.DataFrame, numeric_cols: List[str] = None, title: str = 'Feature Distributions') -> plt.Figure`

  - Creates distribution plots for numeric features

  - Returns Matplotlib figure object

- `plot_correlation_matrix(df: pd.DataFrame, numeric_cols: List[str] = None, title: str = 'Feature Correlation Matrix') -> plt.Figure`

  - Creates correlation matrix heatmap

  - Returns Matplotlib figure object

- `plot_model_performance(model_results: Dict[str, Dict[str, float]], title: str = 'Model Performance Comparison') -> plt.Figure`

  - Creates model performance comparison plots

  - Returns Matplotlib figure object

## Main Pipeline

### RentalPricePipeline

Main pipeline for rental price prediction.

#### Methods

- `run_full_pipeline(cities: List[str] = None, download_data: bool = True, extract_pois: bool = True, train_models: bool = True, create_visualizations: bool = True) -> Dict[str, Any]`

  - Runs the complete machine learning pipeline

  - Returns pipeline results

- `predict_prices(new_data: pd.DataFrame) -> pd.Series`

  - Predicts rental prices for new data

  - Returns Series with price predictions

## Configuration

### Configuration Parameters

The system uses a centralized configuration file (`config.py`) with the
following key parameters:

- **Data Sources**: URLs for Airbnb data

- **POI Types**: Points of Interest to extract from OpenStreetMap

- **Feature Engineering**: Grid size, density radius, distance thresholds

- **Model Parameters**: Hyperparameters for all machine learning models

- **Paths**: Directory structure for data, models, and reports

- **Logging**: Logging configuration and file paths

### Environment Variables

The system can be configured using environment variables:

- `RENTAL_DATA_DIR`: Directory for data files

- `RENTAL_MODELS_DIR`: Directory for model files

- `RENTAL_REPORTS_DIR`: Directory for report files

- `RENTAL_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Error Handling

The system includes comprehensive error handling:

- **Data Loading**: Handles missing files, network errors, and data corruption

- **POI Extraction**: Handles network issues and OSMnx configuration problems

- **Feature Engineering**: Handles missing data and invalid coordinates

- **Model Training**: Handles training failures and hyperparameter issues

- **Visualization**: Handles missing data and plotting errors

## Logging

The system uses Python's logging module with the following features:

- **Multiple Handlers**: Console and file logging

- **Configurable Levels**: DEBUG, INFO, WARNING, ERROR

- **Structured Logging**: Consistent format across all modules

- **Error Tracking**: Detailed error information for debugging

## Testing

The system includes comprehensive unit tests:

- **Data Loading Tests**: Test data loading and validation

- **Feature Engineering Tests**: Test feature creation and processing

- **Model Tests**: Test model training and evaluation

- **Visualization Tests**: Test plotting and mapping functionality

Run tests using:

```bash
pytest
pytest --cov=src
pytest tests/test_data_loader.py

```
