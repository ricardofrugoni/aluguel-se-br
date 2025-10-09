# Rental Price Prediction System - Project Summary

## 🎯 Project Overview

A comprehensive machine learning system for predicting **short-term rental
prices (daily rates)** in São Paulo and Rio de Janeiro using geospatial
features, seasonal patterns, review intelligence, and amenity analysis. Designed
specifically for Airbnb-style vacation rentals. The system is designed to be
**professional**, **well-documented**, and **reproducible**.

## 🏗️ Architecture

### Core Components

1. **Data Pipeline**

   - Automated data loading from Inside Airbnb

   - Data cleaning and preprocessing

   - POI extraction from OpenStreetMap

   - Feature engineering with geospatial data

2. **Machine Learning Pipeline**

   - Baseline models (Ridge, Random Forest)

   - Advanced models (XGBoost, LightGBM, CatBoost)

   - Ensemble learning with weighted averaging

   - Comprehensive model evaluation

3. **Visualization & Analysis**

   - Interactive maps with Folium

   - Data analysis plots with Matplotlib/Seaborn

   - Model performance visualizations

   - Geospatial analysis tools

### Short-Term Rental Specific Features

- **Temporal Analysis**: Seasonal patterns, weekend pricing, holiday premiums

- **Review Analytics**: Trust scores, host reputation, rating consistency

- **Amenity Intelligence**: Parse and score 50+ amenity types

- **Occupancy Optimization**: Predict optimal pricing for maximum occupancy

## 📁 Project Structure

```text

rental-price-sudeste/
├── 📁 data/                    # Data storage

│   ├── raw/                   # Original data files

│   ├── processed/             # Cleaned data

│   └── external/              # POI data

├── 📁 src/                     # Source code

│   ├── data/                  # Data loading & processing

│   ├── features/              # Feature engineering

│   ├── models/                # ML models

│   └── visualization/         # Maps & plots

├── 📁 tests/                    # Unit tests

├── 📁 docs/                    # Documentation

├── 📁 notebooks/               # Jupyter notebooks

├── 📁 models/                  # Trained models

├── 📁 reports/                 # Output reports

├── 📁 logs/                    # Log files

├── 🐍 main.py                  # Main pipeline

├── ⚙️ config.py               # Configuration

├── 📋 requirements.txt         # Dependencies

└── 📖 README.md               # Project documentation

```

## 🚀 Key Features

### Data Processing

- **Automated Data Loading**: Downloads Airbnb data from Inside Airbnb

- **Data Validation**: Comprehensive data quality checks

- **POI Extraction**: Points of Interest from OpenStreetMap

- **Feature Engineering**: 20+ geospatial features

### Machine Learning

- **Multiple Models**: 6 different ML algorithms

- **Ensemble Learning**: Weighted combination of models

- **Cross-Validation**: 5-fold stratified validation

- **Hyperparameter Tuning**: Grid search optimization

### Visualization

- **Interactive Maps**: Property locations, POIs, predictions

- **Data Analysis**: Distributions, correlations, feature importance

- **Model Performance**: Comparison charts, residual analysis

- **Geospatial Analysis**: Price heatmaps, density plots

## 🛠️ Technology Stack

### Core Libraries

- **Python 3.8+**: Main programming language

- **pandas, numpy**: Data manipulation

- **geopandas, shapely**: Geospatial data processing

- **osmnx**: OpenStreetMap data extraction

### Machine Learning

- **scikit-learn**: Baseline models and evaluation

- **xgboost**: Gradient boosting

- **lightgbm**: Light gradient boosting

- **catboost**: Categorical boosting

### Visualization

- **folium**: Interactive maps

- **matplotlib, seaborn**: Data visualization

- **shap**: Model interpretability

### Development

- **pytest**: Testing framework

- **black**: Code formatting

- **flake8**: Code linting

## 📊 Data Sources

### Primary Data

- **Inside Airbnb**: Rental listings for São Paulo and Rio de Janeiro

- **OpenStreetMap**: Points of Interest (subway, supermarket, school, hospital, mall)

### Feature Types

1. **Distance Features**: Distance to nearest POIs

2. **Density Features**: POI counts within 1km radius

3. **Grid Features**: Aggregated statistics by grid cells

4. **Accessibility Scores**: Transportation and amenity accessibility

5. **Interaction Features**: Combinations of basic features

## 🎯 Model Performance

### Evaluation Metrics

- **MAE**: Mean Absolute Error

- **RMSE**: Root Mean Square Error

- **R²**: Coefficient of Determination

- **MAPE**: Mean Absolute Percentage Error

- **Within 10%/20%**: Accuracy within percentage ranges

### Model Comparison

- **Baseline Models**: Ridge Regression, Random Forest

- **Advanced Models**: XGBoost, LightGBM, CatBoost

- **Ensemble Model**: Weighted average of all models

## 🔧 Configuration

### Key Parameters

- **Grid Size**: 0.01 degrees for spatial aggregation

- **Density Radius**: 1km for POI density calculation

- **Distance Threshold**: 10km maximum distance to POIs

- **Cross-Validation**: 5-fold stratified by grid

### Customization

- **Cities**: Configurable city selection

- **POI Types**: Customizable Points of Interest

- **Model Parameters**: Adjustable hyperparameters

- **Feature Engineering**: Configurable feature creation

## 📈 Usage Examples

### Quick Start

```bash

# Run complete pipeline

python main.py

# Run with custom options

python main.py --cities sao_paulo rio_de_janeiro --no-download

```text

### Individual Components

```python
from src.data.data_loader import DataLoader
from src.models.baseline_models import BaselineModels

# Load data

loader = DataLoader()
data = loader.load_multiple_cities(['sao_paulo'])

# Train models

baseline = BaselineModels()
metrics = baseline.train_all_baseline_models(X_train, y_train, X_test, y_test)

```text

## 🧪 Testing

### Test Coverage

- **Unit Tests**: Individual component testing

- **Integration Tests**: End-to-end pipeline testing

- **Data Validation**: Data quality and format testing

- **Model Testing**: Model training and evaluation testing

### Running Tests

```bash

# Run all tests

pytest

# Run with coverage

pytest --cov=src

# Run specific test file

pytest tests/test_data_loader.py

```text

## 📚 Documentation

### Available Documentation

- **README.md**: Project overview and quick start

- **docs/API_REFERENCE.md**: Detailed API documentation

- **docs/INSTALLATION.md**: Installation and setup guide

- **notebooks/**: Jupyter notebooks for analysis

- **example_usage.py**: Usage examples

### Code Documentation

- **Type Hints**: All functions include type annotations

- **Docstrings**: Google-style docstrings for all classes and methods

- **Comments**: Explanatory comments for complex logic

- **Logging**: Comprehensive logging throughout the system

## 🔄 Workflow

### Complete Pipeline

1. **Data Loading**: Download and validate Airbnb data

2. **Data Processing**: Clean and preprocess data

3. **POI Extraction**: Extract Points of Interest from OpenStreetMap

4. **Feature Engineering**: Create geospatial features

5. **Model Training**: Train baseline, advanced, and ensemble models

6. **Model Evaluation**: Comprehensive model comparison

7. **Visualization**: Create maps and analysis plots

8. **Report Generation**: Generate final project report

### Individual Steps

- Each component can be run independently

- Modular design allows for custom workflows

- Configuration-driven approach for flexibility

## 🎨 Outputs

### Generated Files

- **Processed Data**: Cleaned and featured datasets

- **Trained Models**: Saved model files (.pkl)

- **Visualizations**: Interactive maps (.html) and plots (.png)

- **Reports**: JSON reports with results and metrics

- **Logs**: Detailed execution logs

### Interactive Maps

- **Property Map**: Rental properties with price coloring

- **POI Map**: Points of Interest with different markers

- **Prediction Map**: Price predictions visualization

- **Combined Map**: Properties and POIs together

## 🚀 Getting Started

### Installation

```bash

# Clone repository

git clone <repository-url>
cd rental-price-sudeste

# Create virtual environment

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies

pip install -r requirements.txt

# Run example

python example_usage.py

```text

### Quick Test

```bash

# Run basic pipeline

python main.py --cities sao_paulo --no-download --no-pois

# Run tests

pytest tests/ -v

# Check installation

python -c "import src; print('Installation successful!')"

```

## 🎯 Project Goals

### Primary Objectives

- **Accurate Predictions**: High-quality rental price predictions

- **Geospatial Features**: Leverage location-based information

- **Model Comparison**: Comprehensive model evaluation

- **Reproducibility**: Consistent and repeatable results

### Secondary Objectives

- **Professional Code**: Clean, documented, and tested code

- **Modular Design**: Reusable and extensible components

- **Visualization**: Clear and informative visualizations

- **Documentation**: Comprehensive user and developer documentation

## 🔮 Future Enhancements

### Potential Improvements

- **Additional Cities**: Expand to more Brazilian cities

- **Real-time Data**: Live data updates and predictions

- **Web Interface**: User-friendly web application

- **API Endpoints**: RESTful API for predictions

- **Advanced Features**: Time series, seasonality, market trends

### Technical Enhancements

- **Model Optimization**: Advanced hyperparameter tuning

- **Feature Selection**: Automated feature selection

- **Ensemble Methods**: More sophisticated ensemble techniques

- **Deep Learning**: Neural network models

- **Cloud Deployment**: Scalable cloud infrastructure

## 📞 Support

### Getting Help

- **Documentation**: Check README.md and docs/ directory

- **Examples**: Run example_usage.py and run_example.py

- **Tests**: Check test files for usage patterns

- **Issues**: Open GitHub issues for bugs and questions

### Contributing

- **Code Quality**: Follow PEP 8 and use type hints

- **Testing**: Add tests for new functionality

- **Documentation**: Update documentation for changes

- **Pull Requests**: Submit PRs for new features

---

## This project represents a complete, production-ready machine learning system for rental price prediction, demonstrating best practices in data science, software engineering, and project organization.
