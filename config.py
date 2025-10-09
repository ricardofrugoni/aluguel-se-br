"""
Configuration file for rental price prediction project.
Contains all paths, parameters, and constants.
"""

from pathlib import Path
from typing import Dict, List

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXTERNAL_DATA_DIR = DATA_DIR / "external"
MODELS_DIR = PROJECT_ROOT / "models"
REPORTS_DIR = PROJECT_ROOT / "reports"
NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

# Create directories if they don't exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, EXTERNAL_DATA_DIR, 
                 MODELS_DIR, REPORTS_DIR, NOTEBOOKS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Data sources
AIRBNB_DATA_URLS = {
    "sao_paulo": "http://data.insideairbnb.com/brazil/sp/sao-paulo/2024-01-01/data/listings.csv.gz",
    "rio_de_janeiro": "http://data.insideairbnb.com/brazil/rj/rio-de-janeiro/2024-01-01/data/listings.csv.gz"
}

# POI types to extract from OpenStreetMap
POI_TYPES = {
    "subway": {"amenity": "subway_entrance"},
    "bus_station": {"amenity": "bus_station"},
    "tourist_attraction": {"tourism": "attraction"},
    "beach": {"natural": "beach"},
    "viewpoint": {"tourism": "viewpoint"},
    "museum": {"tourism": "museum"},
    "park": {"leisure": "park"},
    "restaurant": {"amenity": "restaurant"},
    "bar": {"amenity": "bar"},
    "cafe": {"amenity": "cafe"},
    "supermarket": {"shop": "supermarket"},
    "hospital": {"amenity": "hospital"},
    "shopping_mall": {"shop": "mall"}
}

# Seasonal/Temporal features configuration
SEASONAL_CONFIG = {
    "enable_temporal_features": True,
    "enable_review_features": True,
    "enable_amenity_parsing": True,
    "enable_host_features": True
}

# Amenity categories for parsing
AMENITY_CATEGORIES = {
    "essential": ["Wifi", "Internet", "Wireless Internet", "Kitchen", "Air conditioning", "Heating", "TV", "Cable TV", "Hot water"],
    "premium": ["Pool", "Swimming pool", "Gym", "Elevator", "Doorman", "Free parking", "Washer", "Dryer"],
    "work_friendly": ["Laptop friendly workspace", "Desk", "Ethernet connection", "Printer"]
}

TARGET_VARIABLE = "price"
MIN_REVIEWS_FOR_TRUST = 5
MAJOR_HOLIDAYS = [(1, 1), (4, 21), (5, 1), (9, 7), (10, 12), (11, 2), (11, 15), (12, 25)]

# Feature engineering parameters
GRID_SIZE = 0.01  # degrees
DENSITY_RADIUS_KM = 1.0  # km
DISTANCE_THRESHOLD_KM = 10.0  # km

# Model parameters
RANDOM_STATE = 42
CV_FOLDS = 5
TEST_SIZE = 0.2

# Baseline models
BASELINE_MODELS = {
    "ridge": {"alpha": 1.0},
    "random_forest": {"n_estimators": 100, "random_state": RANDOM_STATE}
}

# Advanced models
ADVANCED_MODELS = {
    "xgboost": {
        "n_estimators": 1000,
        "learning_rate": 0.1,
        "max_depth": 6,
        "random_state": RANDOM_STATE
    },
    "lightgbm": {
        "n_estimators": 1000,
        "learning_rate": 0.1,
        "max_depth": 6,
        "random_state": RANDOM_STATE,
        "verbose": -1
    },
    "catboost": {
        "iterations": 1000,
        "learning_rate": 0.1,
        "depth": 6,
        "random_seed": RANDOM_STATE,
        "verbose": False
    }
}

# Evaluation metrics
METRICS = ["mae", "rmse", "r2", "mape", "within_10pct", "within_20pct"]

# Logging configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
    },
    "handlers": {
        "default": {
            "level": "INFO",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
        "file": {
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.FileHandler",
            "filename": PROJECT_ROOT / "logs" / "rental_prediction.log",
            "mode": "a",
        },
    },
    "loggers": {
        "": {
            "handlers": ["default", "file"],
            "level": "DEBUG",
            "propagate": False
        }
    }
}
