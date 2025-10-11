"""
Unit tests for baseline models module.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil

from src.models.baseline_models import BaselineModels


class TestBaselineModels:
    """Test cases for BaselineModels class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.baseline = BaselineModels(self.temp_dir)
        
        # Create sample data
        np.random.seed(42)
        n_samples = 100
        n_features = 5
        
        self.X_train = pd.DataFrame(np.random.randn(n_samples, n_features))
        self.y_train = pd.Series(np.random.randn(n_samples))
        self.X_test = pd.DataFrame(np.random.randn(20, n_features))
        self.y_test = pd.Series(np.random.randn(20))
    
    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)
    
    def test_train_ridge_regression(self):
        """Test Ridge Regression training."""
        metrics = self.baseline.train_ridge_regression(
            self.X_train, self.y_train, self.X_test, self.y_test
        )
        
        # Check that metrics were calculated
        assert 'train_mae' in metrics
        assert 'test_mae' in metrics
        assert 'train_r2' in metrics
        assert 'test_r2' in metrics
        assert 'train_mape' in metrics
        assert 'test_mape' in metrics
        
        # Check that metrics are reasonable
        assert metrics['train_mae'] >= 0
        assert metrics['test_mae'] >= 0
        assert metrics['train_r2'] <= 1.0
        assert metrics['test_r2'] <= 1.0
        
        # Check that model was stored
        assert 'ridge' in self.baseline.trained_models
        assert 'ridge' in self.baseline.model_scores
    
    def test_train_random_forest(self):
        """Test Random Forest training."""
        metrics = self.baseline.train_random_forest(
            self.X_train, self.y_train, self.X_test, self.y_test
        )
        
        # Check that metrics were calculated
        assert 'train_mae' in metrics
        assert 'test_mae' in metrics
        assert 'train_r2' in metrics
        assert 'test_r2' in metrics
        
        # Check that metrics are reasonable
        assert metrics['train_mae'] >= 0
        assert metrics['test_mae'] >= 0
        assert metrics['train_r2'] <= 1.0
        assert metrics['test_r2'] <= 1.0
        
        # Check that model was stored
        assert 'random_forest' in self.baseline.trained_models
        assert 'random_forest' in self.baseline.model_scores
    
    def test_train_all_baseline_models(self):
        """Test training all baseline models."""
        all_metrics = self.baseline.train_all_baseline_models(
            self.X_train, self.y_train, self.X_test, self.y_test
        )
        
        # Check that both models were trained
        assert 'ridge' in all_metrics
        assert 'random_forest' in all_metrics
        
        # Check that metrics were calculated for both models
        assert 'test_r2' in all_metrics['ridge']
        assert 'test_mae' in all_metrics['ridge']
        assert 'test_r2' in all_metrics['random_forest']
        assert 'test_mae' in all_metrics['random_forest']
    
    def test_hyperparameter_tuning(self):
        """Test hyperparameter tuning functionality."""
        # Train a model first
        self.baseline.train_ridge_regression(
            self.X_train, self.y_train, self.X_test, self.y_test
        )
        
        # Define parameter grid
        param_grid = {
            'alpha': [0.1, 1.0, 10.0]
        }
        
        # Perform hyperparameter tuning
        results = self.baseline.hyperparameter_tuning(
            self.X_train, self.y_train, 'ridge', param_grid
        )
        
        # Check that results were returned
        assert 'best_params' in results
        assert 'best_score' in results
        assert 'cv_results' in results
        
        # Check that best parameters are reasonable
        assert 'alpha' in results['best_params']
        assert results['best_params']['alpha'] in [0.1, 1.0, 10.0]
    
    def test_cross_validate_model(self):
        """Test cross-validation functionality."""
        # Train a model first
        self.baseline.train_ridge_regression(
            self.X_train, self.y_train, self.X_test, self.y_test
        )
        
        # Perform cross-validation
        cv_results = self.baseline.cross_validate_model(
            self.X_train, self.y_train, 'ridge'
        )
        
        # Check that results were returned
        assert 'cv_scores' in cv_results
        assert 'cv_mean' in cv_results
        assert 'cv_std' in cv_results
        assert 'cv_folds' in cv_results
        
        # Check that results are reasonable
        assert len(cv_results['cv_scores']) == 5  # Default CV folds
        assert cv_results['cv_mean'] is not None
        assert cv_results['cv_std'] >= 0
    
    def test_get_feature_importance(self):
        """Test feature importance extraction."""
        # Train a model first
        self.baseline.train_random_forest(
            self.X_train, self.y_train, self.X_test, self.y_test
        )
        
        # Get feature importance
        feature_names = [f'feature_{i}' for i in range(self.X_train.shape[1])]
        importance_df = self.baseline.get_feature_importance('random_forest', feature_names)
        
        # Check that importance was calculated
        assert len(importance_df) == len(feature_names)
        assert 'feature' in importance_df.columns
        assert 'importance' in importance_df.columns
        
        # Check that importance values are non-negative
        assert (importance_df['importance'] >= 0).all()
        
        # Check that importance sums to 1 (for Random Forest)
        assert abs(importance_df['importance'].sum() - 1.0) < 1e-6
    
    def test_get_feature_importance_linear_model(self):
        """Test feature importance for linear model."""
        # Train a model first
        self.baseline.train_ridge_regression(
            self.X_train, self.y_train, self.X_test, self.y_test
        )
        
        # Get feature importance
        feature_names = [f'feature_{i}' for i in range(self.X_train.shape[1])]
        importance_df = self.baseline.get_feature_importance('ridge', feature_names)
        
        # Check that importance was calculated
        assert len(importance_df) == len(feature_names)
        assert 'feature' in importance_df.columns
        assert 'importance' in importance_df.columns
        
        # Check that importance values are non-negative
        assert (importance_df['importance'] >= 0).all()
    
    def test_save_models(self):
        """Test model saving functionality."""
        # Train a model first
        self.baseline.train_ridge_regression(
            self.X_train, self.y_train, self.X_test, self.y_test
        )
        
        # Save models
        saved_files = self.baseline.save_models('test_baseline')
        
        # Check that files were saved
        assert 'ridge' in saved_files
        assert 'scores' in saved_files
        
        # Check that files exist
        assert saved_files['ridge'].exists()
        assert saved_files['scores'].exists()
    
    def test_load_models(self):
        """Test model loading functionality."""
        # Train and save a model first
        self.baseline.train_ridge_regression(
            self.X_train, self.y_train, self.X_test, self.y_test
        )
        self.baseline.save_models('test_baseline')
        
        # Load models
        loaded_models = self.baseline.load_models('test_baseline')
        
        # Check that models were loaded
        assert 'ridge' in loaded_models
        assert 'scores' in loaded_models
        
        # Check that loaded model can make predictions
        loaded_model = loaded_models['ridge']
        predictions = loaded_model.predict(self.X_test)
        assert len(predictions) == len(self.y_test)
    
    def test_calculate_metrics(self):
        """Test metrics calculation."""
        # Create sample predictions
        y_true = pd.Series([1, 2, 3, 4, 5])
        y_pred = pd.Series([1.1, 1.9, 3.1, 3.9, 5.1])
        
        # Calculate metrics
        metrics = self.baseline._calculate_metrics(y_true, y_pred, y_true, y_pred)
        
        # Check that all expected metrics are present
        expected_metrics = [
            'train_mae', 'train_rmse', 'train_r2',
            'test_mae', 'test_rmse', 'test_r2',
            'train_mape', 'test_mape',
            'train_within_10pct', 'test_within_10pct',
            'train_within_20pct', 'test_within_20pct'
        ]
        
        for metric in expected_metrics:
            assert metric in metrics
            assert isinstance(metrics[metric], (int, float))
    
    def test_baseline_models_initialization(self):
        """Test BaselineModels initialization."""
        assert self.baseline.models_dir == self.temp_dir
        assert self.baseline.logger is not None
        assert isinstance(self.baseline.trained_models, dict)
        assert isinstance(self.baseline.model_scores, dict)
    
    def test_baseline_models_custom_directory(self):
        """Test BaselineModels with custom directory."""
        custom_dir = Path(tempfile.mkdtemp())
        baseline = BaselineModels(custom_dir)
        
        assert baseline.models_dir == custom_dir
        assert custom_dir.exists()
        
        # Clean up
        shutil.rmtree(custom_dir)
    
    def test_feature_importance_unsupported_model(self):
        """Test feature importance with unsupported model."""
        # Train a model first
        self.baseline.train_ridge_regression(
            self.X_train, self.y_train, self.X_test, self.y_test
        )
        
        # Try to get feature importance for unsupported model
        with pytest.raises(ValueError):
            self.baseline.get_feature_importance('nonexistent_model', ['feature1'])
    
    def test_cross_validate_untrained_model(self):
        """Test cross-validation with untrained model."""
        with pytest.raises(ValueError):
            self.baseline.cross_validate_model(self.X_train, self.y_train, 'nonexistent_model')
    
    def test_hyperparameter_tuning_unknown_model(self):
        """Test hyperparameter tuning with unknown model."""
        with pytest.raises(ValueError):
            self.baseline.hyperparameter_tuning(
                self.X_train, self.y_train, 'unknown_model', {'param': [1, 2, 3]}
            )


if __name__ == "__main__":
    pytest.main([__file__])


