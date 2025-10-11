"""
Review feature engineering for short-term rental price prediction.
Handles review scores, host features, and trust indicators.
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class ReviewFeatureEngineer:
    """
    Creates review and host features for short-term rental price prediction.
    
    Attributes:
        min_reviews: Minimum number of reviews for trust calculation
        logger: Logger instance for tracking operations
    """
    
    def __init__(self, min_reviews: int = 5):
        """
        Initialize ReviewFeatureEngineer.
        
        Args:
            min_reviews: Minimum number of reviews for trust calculation.
        """
        self.min_reviews = min_reviews
        self.logger = logging.getLogger(__name__)
    
    def add_all_review_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add all review and host features to the dataset.
        
        Args:
            df: DataFrame with rental data.
            
        Returns:
            DataFrame with review features added.
        """
        self.logger.info("Adding all review features")
        df = df.copy()
        
        df = self.add_review_features(df)
        df = self.add_host_features(df)
        
        self.logger.info(f"Review features added. Total columns: {len(df.columns)}")
        return df
    
    def add_review_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add review-based features.
        
        Args:
            df: DataFrame with rental data.
            
        Returns:
            DataFrame with review features added.
        """
        df = df.copy()
        
        # Normalize rating to 0-1 scale
        if 'review_scores_rating' in df.columns:
            df['rating_normalized'] = (df['review_scores_rating'] / 10).clip(0, 1)
        
        # Review count features
        if 'number_of_reviews' in df.columns:
            df['has_enough_reviews'] = (df['number_of_reviews'] >= self.min_reviews).astype(int)
            df['reviews_log'] = np.log1p(df['number_of_reviews'])
        
        # Detailed rating analysis
        review_cols = [
            'review_scores_accuracy', 'review_scores_cleanliness', 
            'review_scores_checkin', 'review_scores_communication', 
            'review_scores_location', 'review_scores_value'
        ]
        available_cols = [col for col in review_cols if col in df.columns]
        
        if available_cols:
            df['avg_detailed_rating'] = df[available_cols].mean(axis=1)
            df['rating_consistency'] = df[available_cols].std(axis=1).fillna(0)
            df['rating_quality'] = 10 - df['rating_consistency']
        
        # Trust score calculation
        trust_components = []
        if 'rating_normalized' in df.columns:
            trust_components.append(df['rating_normalized'].fillna(0) * 0.4)
        if 'number_of_reviews' in df.columns:
            trust_components.append((df['number_of_reviews'].fillna(0) / 100).clip(0, 1) * 0.3)
        if 'has_enough_reviews' in df.columns:
            trust_components.append(df['has_enough_reviews'] * 0.3)
        
        if trust_components:
            df['trust_score'] = sum(trust_components)
        
        # Review frequency
        if 'reviews_per_month' in df.columns:
            df['review_frequency'] = df['reviews_per_month'].fillna(0)
        
        return df
    
    def add_host_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add host-based features.
        
        Args:
            df: DataFrame with rental data.
            
        Returns:
            DataFrame with host features added.
        """
        df = df.copy()
        
        # Host experience
        if 'host_since' in df.columns:
            df['host_since'] = pd.to_datetime(df['host_since'], errors='coerce')
            df['host_experience_days'] = (pd.to_datetime('today') - df['host_since']).dt.days
            df['host_experience_years'] = df['host_experience_days'] / 365.25
            df['host_experience_capped'] = df['host_experience_years'].clip(0, 5)
        
        # Host status features
        if 'host_is_superhost' in df.columns:
            df['is_superhost_num'] = (df['host_is_superhost'] == 't').astype(int)
        
        if 'host_identity_verified' in df.columns:
            df['is_verified_num'] = (df['host_identity_verified'] == 't').astype(int)
        
        # Host response rates
        if 'host_response_rate' in df.columns:
            df['host_response_rate_num'] = pd.to_numeric(
                df['host_response_rate'].str.rstrip('%'), errors='coerce'
            ) / 100
        
        if 'host_acceptance_rate' in df.columns:
            df['host_acceptance_rate_num'] = pd.to_numeric(
                df['host_acceptance_rate'].str.rstrip('%'), errors='coerce'
            ) / 100
        
        # Professional host indicator
        if 'host_listings_count' in df.columns:
            df['is_professional_host'] = (df['host_listings_count'] > 3).astype(int)
        
        # Host quality score
        quality_components = []
        if 'is_superhost_num' in df.columns:
            quality_components.append(df['is_superhost_num'] * 0.4)
        if 'host_response_rate_num' in df.columns:
            quality_components.append(df['host_response_rate_num'].fillna(0) * 0.25)
        if 'is_verified_num' in df.columns:
            quality_components.append(df['is_verified_num'] * 0.2)
        if 'host_experience_capped' in df.columns:
            quality_components.append((df['host_experience_capped'] / 5) * 0.15)
        
        if quality_components:
            df['host_quality_score'] = sum(quality_components)
        
        return df


def main():
    """
    Example usage of ReviewFeatureEngineer.
    """
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize review feature engineer
    review_engineer = ReviewFeatureEngineer(min_reviews=5)
    
    # Example with sample data
    sample_data = pd.DataFrame({
        'review_scores_rating': [4.8, 4.5, 4.9],
        'number_of_reviews': [50, 20, 100],
        'reviews_per_month': [2.5, 1.0, 4.0],
        'host_is_superhost': ['t', 'f', 't'],
        'host_identity_verified': ['t', 't', 'f'],
        'host_response_rate': ['100%', '95%', '98%'],
        'host_listings_count': [1, 5, 2]
    })
    
    # Add review features
    featured_data = review_engineer.add_all_review_features(sample_data)
    print("Review features added:")
    print(featured_data.columns.tolist())


if __name__ == "__main__":
    main()


