"""
Example usage of the rental price prediction system for short-term rentals.
Demonstrates the new temporal, review, and amenity features.
"""

import logging
import pandas as pd
import numpy as np
from pathlib import Path

# Import project modules
from src.features.temporal_features import TemporalFeatureEngineer
from src.features.review_features import ReviewFeatureEngineer
from src.features.amenity_features import AmenityFeatureEngineer
from src.features.feature_engineer import FeatureEngineer
from config import AMENITY_CATEGORIES, MIN_REVIEWS_FOR_TRUST, MAJOR_HOLIDAYS

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_temporal_features():
    """Example of temporal feature engineering."""
    print("=== Temporal Features Example ===")
    
    # Create sample data with availability and review patterns
    sample_data = pd.DataFrame({
        'availability_30': [10, 5, 20, 15],
        'availability_60': [20, 10, 40, 30],
        'availability_90': [30, 15, 60, 45],
        'reviews_per_month': [2.5, 1.0, 4.0, 3.2],
        'number_of_reviews': [50, 20, 100, 75]
    })
    
    # Initialize temporal feature engineer
    temporal_engineer = TemporalFeatureEngineer(holidays=MAJOR_HOLIDAYS)
    
    # Add temporal features
    featured_data = temporal_engineer.add_all_temporal_features(sample_data)
    
    print(f"Original columns: {list(sample_data.columns)}")
    print(f"New temporal features: {[col for col in featured_data.columns if col not in sample_data.columns]}")
    print(f"Total features: {len(featured_data.columns)}")
    
    # Show some key features
    if 'season' in featured_data.columns:
        print(f"Seasons: {featured_data['season'].unique()}")
    if 'is_high_season' in featured_data.columns:
        print(f"High season properties: {featured_data['is_high_season'].sum()}")
    if 'occupancy_rate_30' in featured_data.columns:
        print(f"Average occupancy rate: {featured_data['occupancy_rate_30'].mean():.2f}")


def example_review_features():
    """Example of review feature engineering."""
    print("\n=== Review Features Example ===")
    
    # Create sample data with review and host information
    sample_data = pd.DataFrame({
        'review_scores_rating': [4.8, 4.5, 4.9, 4.2],
        'number_of_reviews': [50, 20, 100, 15],
        'reviews_per_month': [2.5, 1.0, 4.0, 0.8],
        'review_scores_accuracy': [4.9, 4.6, 5.0, 4.3],
        'review_scores_cleanliness': [4.7, 4.4, 4.8, 4.1],
        'review_scores_checkin': [4.8, 4.5, 4.9, 4.2],
        'review_scores_communication': [4.9, 4.6, 5.0, 4.3],
        'review_scores_location': [4.6, 4.3, 4.7, 4.0],
        'review_scores_value': [4.5, 4.2, 4.6, 3.9],
        'host_is_superhost': ['t', 'f', 't', 'f'],
        'host_identity_verified': ['t', 't', 'f', 't'],
        'host_response_rate': ['100%', '95%', '98%', '90%'],
        'host_acceptance_rate': ['95%', '90%', '98%', '85%'],
        'host_listings_count': [1, 5, 2, 8],
        'host_since': ['2020-01-15', '2019-06-20', '2021-03-10', '2018-12-05']
    })
    
    # Initialize review feature engineer
    review_engineer = ReviewFeatureEngineer(min_reviews=MIN_REVIEWS_FOR_TRUST)
    
    # Add review features
    featured_data = review_engineer.add_all_review_features(sample_data)
    
    print(f"Original columns: {list(sample_data.columns)}")
    print(f"New review features: {[col for col in featured_data.columns if col not in sample_data.columns]}")
    print(f"Total features: {len(featured_data.columns)}")
    
    # Show some key features
    if 'trust_score' in featured_data.columns:
        print(f"Average trust score: {featured_data['trust_score'].mean():.2f}")
    if 'host_quality_score' in featured_data.columns:
        print(f"Average host quality score: {featured_data['host_quality_score'].mean():.2f}")
    if 'is_superhost_num' in featured_data.columns:
        print(f"Superhosts: {featured_data['is_superhost_num'].sum()}")


def example_amenity_features():
    """Example of amenity feature engineering."""
    print("\n=== Amenity Features Example ===")
    
    # Create sample data with amenity strings
    sample_data = pd.DataFrame({
        'amenities': [
            '["Wifi", "Kitchen", "Air conditioning", "TV", "Cable TV", "Hot water"]',
            '["Pool", "Gym", "Elevator", "Free parking", "Washer", "Dryer"]',
            '["Wifi", "Laptop friendly workspace", "Desk", "Printer", "Ethernet connection"]',
            '["Kitchen", "Air conditioning", "TV", "Free parking", "Washer"]'
        ]
    })
    
    # Initialize amenity feature engineer
    amenity_engineer = AmenityFeatureEngineer(amenity_categories=AMENITY_CATEGORIES)
    
    # Add amenity features
    featured_data = amenity_engineer.add_amenity_features(sample_data)
    
    print(f"Original columns: {list(sample_data.columns)}")
    print(f"New amenity features: {[col for col in featured_data.columns if col not in sample_data.columns]}")
    print(f"Total features: {len(featured_data.columns)}")
    
    # Show some key features
    if 'amenities_count' in featured_data.columns:
        print(f"Average amenities count: {featured_data['amenities_count'].mean():.1f}")
    if 'amenity_score' in featured_data.columns:
        print(f"Average amenity score: {featured_data['amenity_score'].mean():.2f}")
    if 'has_essential' in featured_data.columns:
        print(f"Properties with essential amenities: {featured_data['has_essential'].sum()}")
    if 'has_premium' in featured_data.columns:
        print(f"Properties with premium amenities: {featured_data['has_premium'].sum()}")


def example_comprehensive_features():
    """Example of comprehensive feature engineering."""
    print("\n=== Comprehensive Features Example ===")
    
    # Create comprehensive sample data
    sample_data = pd.DataFrame({
        'latitude': [-23.5505, -22.9068, -23.5505, -22.9000],
        'longitude': [-46.6333, -43.1729, -46.6333, -43.1500],
        'price': [150, 200, 120, 180],
        'bedrooms': [1, 2, 1, 2],
        'bathrooms': [1, 1, 1, 1],
        'availability_30': [10, 5, 20, 15],
        'reviews_per_month': [2.5, 1.0, 4.0, 3.2],
        'number_of_reviews': [50, 20, 100, 75],
        'review_scores_rating': [4.8, 4.5, 4.9, 4.2],
        'host_is_superhost': ['t', 'f', 't', 'f'],
        'amenities': [
            '["Wifi", "Kitchen", "Air conditioning", "TV"]',
            '["Pool", "Gym", "Elevator", "Free parking"]',
            '["Wifi", "Laptop friendly workspace", "Desk"]',
            '["Kitchen", "Air conditioning", "TV", "Free parking"]'
        ]
    })
    
    # Initialize comprehensive feature engineer
    feature_engineer = FeatureEngineer()
    
    # Add all features (without POIs for this example)
    featured_data = feature_engineer.create_all_features(sample_data, pois=None)
    
    print(f"Original columns: {list(sample_data.columns)}")
    print(f"Total features created: {len(featured_data.columns)}")
    
    # Show feature categories
    temporal_features = [col for col in featured_data.columns if col in ['month', 'season', 'is_high_season', 'occupancy_rate_30']]
    review_features = [col for col in featured_data.columns if col in ['trust_score', 'host_quality_score', 'is_superhost_num']]
    amenity_features = [col for col in featured_data.columns if col in ['amenities_count', 'amenity_score', 'has_essential', 'has_premium']]
    
    print(f"Temporal features: {temporal_features}")
    print(f"Review features: {review_features}")
    print(f"Amenity features: {amenity_features}")


def example_short_term_rental_insights():
    """Example of insights specific to short-term rentals."""
    print("\n=== Short-Term Rental Insights ===")
    
    # Create sample data with seasonal patterns
    sample_data = pd.DataFrame({
        'price': [200, 150, 300, 250, 180, 220],
        'month': [12, 3, 1, 7, 9, 6],  # December, March, January, July, September, June
        'review_scores_rating': [4.8, 4.5, 4.9, 4.2, 4.6, 4.7],
        'number_of_reviews': [50, 20, 100, 15, 30, 40],
        'host_is_superhost': ['t', 'f', 't', 'f', 't', 'f'],
        'amenities': [
            '["Wifi", "Kitchen", "Air conditioning", "TV"]',
            '["Wifi", "Kitchen"]',
            '["Pool", "Gym", "Elevator", "Free parking"]',
            '["Wifi", "Kitchen", "TV"]',
            '["Wifi", "Laptop friendly workspace", "Desk"]',
            '["Kitchen", "Air conditioning", "TV", "Free parking"]'
        ]
    })
    
    # Add temporal features
    temporal_engineer = TemporalFeatureEngineer()
    featured_data = temporal_engineer.add_all_temporal_features(sample_data)
    
    # Add review features
    review_engineer = ReviewFeatureEngineer()
    featured_data = review_engineer.add_all_review_features(featured_data)
    
    # Add amenity features
    amenity_engineer = AmenityFeatureEngineer()
    featured_data = amenity_engineer.add_amenity_features(featured_data)
    
    print("Short-term rental insights:")
    print(f"Average price by season:")
    if 'season' in featured_data.columns:
        season_prices = featured_data.groupby('season')['price'].mean()
        for season, avg_price in season_prices.items():
            print(f"  {season}: R$ {avg_price:.2f}")
    
    print(f"\nSuperhost premium:")
    if 'is_superhost_num' in featured_data.columns:
        superhost_prices = featured_data.groupby('is_superhost_num')['price'].mean()
        print(f"  Regular hosts: R$ {superhost_prices[0]:.2f}")
        print(f"  Superhosts: R$ {superhost_prices[1]:.2f}")
        print(f"  Premium: R$ {superhost_prices[1] - superhost_prices[0]:.2f}")
    
    print(f"\nAmenity impact:")
    if 'amenity_score' in featured_data.columns:
        correlation = featured_data['price'].corr(featured_data['amenity_score'])
        print(f"  Price-Amenity Score correlation: {correlation:.3f}")


def main():
    """Run all examples."""
    print("Short-Term Rental Price Prediction System - Feature Examples")
    print("=" * 70)
    
    # Run examples
    example_temporal_features()
    example_review_features()
    example_amenity_features()
    example_comprehensive_features()
    example_short_term_rental_insights()
    
    print("\n" + "=" * 70)
    print("All examples completed!")
    print("\nKey insights for short-term rentals:")
    print("1. Seasonal patterns significantly affect pricing")
    print("2. Review scores and host reputation impact prices")
    print("3. Amenities like WiFi, pool, and workspace add value")
    print("4. Superhost status commands premium pricing")
    print("5. Tourist proximity (beaches, attractions) is crucial")


if __name__ == "__main__":
    main()
