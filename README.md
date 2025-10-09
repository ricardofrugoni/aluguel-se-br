# Rental Price Prediction for Short-Term Rentals (Airbnb) - Southeast Brazil

A comprehensive machine learning system for predicting short-term rental prices
(daily rates) in São Paulo and Rio de Janeiro using geospatial features,
seasonal patterns, reviews, and amenities analysis.

## 🚀 Features

- **Data Processing**: Automated data loading from Inside Airbnb with 75+ features

- **POI Extraction**: Tourist attractions, beaches, restaurants from OpenStreetMap

- **Geospatial Features**: Distances, densities, and grid-based aggregations

- **Temporal Features**: Seasonality, holidays, weekend patterns for vacation rentals

- **Review Intelligence**: Trust scores, host reputation, rating analysis

- **Amenity Analysis**: WiFi, pool, parking impact on pricing

- **Multiple ML Models**: Baseline and Advanced (XGBoost, LightGBM, CatBoost)

- **Ensemble Learning**: Weighted ensemble of all models

- **Interactive Visualizations**: Folium maps and comprehensive data analysis

## Key Differentiators for Short-Term Rentals

- Seasonal pricing patterns (summer peaks, holidays)

- Review and rating impact on pricing

- Host quality and Superhost premium analysis

- Amenity ROI analysis (what amenities increase price)

- Tourist proximity (beaches, attractions, nightlife)

- Occupancy rate optimization

## Target Use Case

This system is specifically designed for **short-term vacation rentals**
(Airbnb-style), not traditional long-term residential rentals. Key differences:

- Target variable: Daily price (not monthly rent)

- Seasonal effects: Summer, holidays, events impact

- Reviews matter: Trust scores and ratings significantly affect pricing

- Amenities premium: Pool, WiFi, workspace add substantial value

- Tourist context: Beach/attraction proximity is crucial

## 📁 Project Structure

```text

rental-price-sudeste/
├── data/
│   ├── raw/           # Original data files

│   ├── processed/     # Cleaned and processed data

│   └── external/      # POI data from OpenStreetMap

├── src/
│   ├── data/         # Data loading and processing

│   ├── features/     # Feature engineering

│   ├── models/       # Machine learning models

│   └── visualization/ # Maps and plots

├── tests/            # Unit tests

├── models/           # Trained models

├── reports/          # Visualizations and reports

├── notebooks/        # Jupyter notebooks for analysis

├── logs/             # Log files

├── main.py           # Main pipeline

├── config.py         # Configuration

└── requirements.txt  # Dependencies

```

## 🛠️ Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd rental-price-sudeste

   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt

   ```

4. **Set up directories**

   ```bash
   python -c "from config import *; print('Directories created')"

   ```text

## 🚀 Quick Start

### Run Complete Pipeline

```bash
python main.py

```text

### Run with Custom Options

```bash

# Process specific cities

python main.py --cities sao_paulo rio_de_janeiro

# Skip data download (use existing data)

python main.py --no-download

# Skip POI extraction

python main.py --no-pois

# Skip model training

python main.py --no-train

# Skip visualizations

python main.py --no-viz

```text

### Run Individual Components

```python
from src.data.data_loader import DataLoader
from src.features.poi_extractor import POIExtractor
from src.models.baseline_models import BaselineModels

# Load data

loader = DataLoader()
data = loader.load_multiple_cities(['sao_paulo', 'rio_de_janeiro'])

# Extract POIs

extractor = POIExtractor()
pois = extractor.extract_pois('sao_paulo')

# Train models

baseline = BaselineModels()
metrics = baseline.train_all_baseline_models(X_train, y_train, X_test, y_test)

```

## 📊 Data Sources

- **Airbnb Data**: Inside Airbnb (http://insideairbnb.com)

- **POI Data**: OpenStreetMap via OSMnx

- **Cities**: São Paulo and Rio de Janeiro

## 🔧 Configuration

Edit `config.py` to customize:

- **Data URLs**: Airbnb data sources

- **POI Types**: Points of Interest to extract

- **Model Parameters**: Hyperparameters for all models

- **Feature Engineering**: Grid size, density radius, etc.

- **Paths**: Directory structure

## 🧪 Testing

Run the test suite:

```bash

# Run all tests

pytest

# Run specific test file

pytest tests/test_data_loader.py

# Run with coverage

pytest --cov=src

```

## 📈 Model Performance

The system includes multiple evaluation metrics:

- **MAE**: Mean Absolute Error

- **RMSE**: Root Mean Square Error

- **R²**: Coefficient of Determination

- **MAPE**: Mean Absolute Percentage Error

- **Within 10%/20%**: Accuracy within percentage ranges

## 🗺️ Visualizations

The system generates:

- **Interactive Maps**: Property locations, POIs, and predictions

- **Data Analysis Plots**: Distributions, correlations, feature importance

- **Model Performance**: Comparison charts and residual analysis

- **Geospatial Analysis**: Price heatmaps and density plots

## 📝 Logging

Comprehensive logging is available in the `logs/` directory:

- **Pipeline logs**: Main execution flow

- **Model logs**: Training and evaluation details

- **Error logs**: Debugging information

## 🤝 Contributing

1. Fork the repository

2. Create a feature branch

3. Make your changes

4. Add tests for new functionality

5. Run the test suite

6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for
details.

## 🙏 Acknowledgments

- Inside Airbnb for providing the dataset

- OpenStreetMap contributors for POI data

- The open-source ML community for excellent libraries

## 📞 Support

For questions or issues:

1. Check the documentation

2. Review the test cases

3. Open an issue on GitHub

4. Contact the development team

## 🔄 Version History

- **v1.0.0**: Initial release with complete pipeline

- **v1.1.0**: Added ensemble learning

- **v1.2.0**: Enhanced visualizations

- **v1.3.0**: Improved feature engineering

---

**Note**: This project is designed for educational and research purposes. Always ensure compliance with data usage terms and local regulations.
