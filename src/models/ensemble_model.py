"""
Ensemble model for combining multiple machine learning models.
Implements weighted average ensemble of baseline and advanced models.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import pickle
import json

from sklearn.ensemble import VotingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from config import MODELS_DIR


class EnsembleModel:
    """
    Ensemble model that combines multiple machine learning models.
    
    Attributes:
        logger: Logger instance for tracking operations
        models_dir: Path to models directory
        ensemble_model: Trained ensemble model
        model_weights: Weights for each model in the ensemble
        ensemble_scores: Performance scores of the ensemble
    """
    
    def __init__(self, models_dir: Optional[Path] = None):
        """
        Initialize EnsembleModel.
        
        Args:
            models_dir: Path to models directory. If None, uses config default.
        """
        self.logger = logging.getLogger(__name__)
        self.models_dir = models_dir or MODELS_DIR
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.ensemble_model = None
        self.model_weights = {}
        self.ensemble_scores = {}
    
    def create_ensemble(self, models: Dict[str, Any], weights: Optional[Dict[str, float]] = None) -> VotingRegressor:
        """
        Create ensemble model from individual models.
        
        Args:
            models: Dictionary mapping model names to trained models.
            weights: Dictionary mapping model names to weights. If None, uses equal weights.
            
        Returns:
            Trained ensemble model.
        """
        self.logger.info("Creating ensemble model")
        
        if not models:
            raise ValueError("No models provided for ensemble")
        
        # Set default weights if not provided
        if weights is None:
            weights = {name: 1.0 / len(models) for name in models.keys()}
        
        # Normalize weights
        total_weight = sum(weights.values())
        normalized_weights = {name: weight / total_weight for name, weight in weights.items()}
        
        # Create voting regressor
        estimators = [(name, model) for name, model in models.items()]
        ensemble = VotingRegressor(estimators=estimators, weights=list(normalized_weights.values()))
        
        self.ensemble_model = ensemble
        self.model_weights = normalized_weights
        
        self.logger.info(f"Created ensemble with {len(models)} models")
        self.logger.info(f"Model weights: {normalized_weights}")
        
        return ensemble
    
    def train_ensemble(self, X_train: pd.DataFrame, y_train: pd.Series,
                      X_test: pd.DataFrame, y_test: pd.Series,
                      models: Dict[str, Any], weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """
        Train ensemble model and evaluate performance.
        
        Args:
            X_train: Training features.
            y_train: Training target.
            X_test: Test features.
            y_test: Test target.
            models: Dictionary mapping model names to trained models.
            weights: Dictionary mapping model names to weights. If None, uses equal weights.
            
        Returns:
            Dictionary with ensemble performance metrics.
        """
        self.logger.info("Training ensemble model")
        
        # Create ensemble
        ensemble = self.create_ensemble(models, weights)
        
        # Train ensemble
        ensemble.fit(X_train, y_train)
        
        # Make predictions
        y_pred_train = ensemble.predict(X_train)
        y_pred_test = ensemble.predict(X_test)
        
        # Calculate metrics
        metrics = self._calculate_metrics(y_train, y_pred_train, y_test, y_pred_test)
        
        # Store ensemble and metrics
        self.ensemble_model = ensemble
        self.ensemble_scores = metrics
        
        self.logger.info(f"Ensemble - Test R²: {metrics['test_r2']:.4f}, Test MAE: {metrics['test_mae']:.4f}")
        
        return metrics
    
    def optimize_weights(self, X_train: pd.DataFrame, y_train: pd.Series,
                        X_val: pd.DataFrame, y_val: pd.Series,
                        models: Dict[str, Any], n_trials: int = 100) -> Dict[str, float]:
        """
        Optimize ensemble weights using validation data.
        
        Args:
            X_train: Training features.
            y_train: Training target.
            X_val: Validation features.
            y_val: Validation target.
            models: Dictionary mapping model names to trained models.
            n_trials: Number of optimization trials.
            
        Returns:
            Dictionary with optimized weights.
        """
        self.logger.info("Optimizing ensemble weights")
        
        best_weights = None
        best_score = float('inf')
        
        for trial in range(n_trials):
            # Generate random weights
            weights = {name: np.random.random() for name in models.keys()}
            
            # Normalize weights
            total_weight = sum(weights.values())
            normalized_weights = {name: weight / total_weight for name, weight in weights.items()}
            
            # Create ensemble with these weights
            ensemble = self.create_ensemble(models, normalized_weights)
            ensemble.fit(X_train, y_train)
            
            # Evaluate on validation set
            y_pred_val = ensemble.predict(X_val)
            val_score = mean_absolute_error(y_val, y_pred_val)
            
            if val_score < best_score:
                best_score = val_score
                best_weights = normalized_weights
        
        self.logger.info(f"Optimized weights: {best_weights}")
        self.logger.info(f"Best validation MAE: {best_score:.4f}")
        
        return best_weights
    
    def get_model_contributions(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Get individual model contributions to ensemble predictions.
        
        Args:
            X: Features to predict.
            
        Returns:
            DataFrame with individual model predictions and contributions.
        """
        if self.ensemble_model is None:
            raise ValueError("Ensemble model not trained. Train it first.")
        
        # Get individual model predictions
        contributions = {}
        
        for name, model in self.ensemble_model.named_estimators_.items():
            predictions = model.predict(X)
            contributions[f'{name}_prediction'] = predictions
            contributions[f'{name}_contribution'] = predictions * self.model_weights[name]
        
        # Add ensemble prediction
        ensemble_pred = self.ensemble_model.predict(X)
        contributions['ensemble_prediction'] = ensemble_pred
        
        return pd.DataFrame(contributions)
    
    def compare_models(self, X_test: pd.DataFrame, y_test: pd.Series,
                      individual_models: Dict[str, Any]) -> pd.DataFrame:
        """
        Compare performance of individual models vs ensemble.
        
        Args:
            X_test: Test features.
            y_test: Test target.
            individual_models: Dictionary mapping model names to trained models.
            
        Returns:
            DataFrame with performance comparison.
        """
        self.logger.info("Comparing individual models vs ensemble")
        
        comparison_results = []
        
        # Evaluate individual models
        for name, model in individual_models.items():
            y_pred = model.predict(X_test)
            
            mae = mean_absolute_error(y_test, y_pred)
            rmse = np.sqrt(mean_squared_error(y_test, y_pred))
            r2 = r2_score(y_test, y_pred)
            
            comparison_results.append({
                'model': name,
                'mae': mae,
                'rmse': rmse,
                'r2': r2,
                'type': 'individual'
            })
        
        # Evaluate ensemble
        if self.ensemble_model is not None:
            y_pred_ensemble = self.ensemble_model.predict(X_test)
            
            mae_ensemble = mean_absolute_error(y_test, y_pred_ensemble)
            rmse_ensemble = np.sqrt(mean_squared_error(y_test, y_pred_ensemble))
            r2_ensemble = r2_score(y_test, y_pred_ensemble)
            
            comparison_results.append({
                'model': 'ensemble',
                'mae': mae_ensemble,
                'rmse': rmse_ensemble,
                'r2': r2_ensemble,
                'type': 'ensemble'
            })
        
        return pd.DataFrame(comparison_results)
    
    def get_ensemble_summary(self) -> Dict[str, Any]:
        """
        Get summary of ensemble model.
        
        Returns:
            Dictionary with ensemble summary.
        """
        if self.ensemble_model is None:
            return {'error': 'Ensemble model not trained'}
        
        summary = {
            'n_models': len(self.ensemble_model.named_estimators_),
            'model_names': list(self.ensemble_model.named_estimators_.keys()),
            'weights': self.model_weights,
            'scores': self.ensemble_scores
        }
        
        return summary
    
    def save_ensemble(self, filename_prefix: str = 'ensemble') -> Dict[str, Path]:
        """
        Save ensemble model to file.
        
        Args:
            filename_prefix: Prefix for saved files.
            
        Returns:
            Dictionary mapping component names to file paths.
        """
        if self.ensemble_model is None:
            raise ValueError("No ensemble model to save. Train it first.")
        
        saved_files = {}
        
        # Save ensemble model
        ensemble_filename = f"{filename_prefix}_model.pkl"
        ensemble_filepath = self.models_dir / ensemble_filename
        
        with open(ensemble_filepath, 'wb') as f:
            pickle.dump(self.ensemble_model, f)
        
        saved_files['ensemble'] = ensemble_filepath
        
        # Save weights and scores
        metadata = {
            'weights': self.model_weights,
            'scores': self.ensemble_scores
        }
        
        metadata_filename = f"{filename_prefix}_metadata.json"
        metadata_filepath = self.models_dir / metadata_filename
        
        with open(metadata_filepath, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
        
        saved_files['metadata'] = metadata_filepath
        
        self.logger.info(f"Saved ensemble model to {ensemble_filepath}")
        self.logger.info(f"Saved ensemble metadata to {metadata_filepath}")
        
        return saved_files
    
    def load_ensemble(self, filename_prefix: str = 'ensemble') -> Dict[str, Any]:
        """
        Load ensemble model from file.
        
        Args:
            filename_prefix: Prefix for saved files.
            
        Returns:
            Dictionary with loaded ensemble components.
        """
        loaded_components = {}
        
        # Load ensemble model
        ensemble_filename = f"{filename_prefix}_model.pkl"
        ensemble_filepath = self.models_dir / ensemble_filename
        
        if ensemble_filepath.exists():
            with open(ensemble_filepath, 'rb') as f:
                loaded_components['ensemble'] = pickle.load(f)
            self.logger.info(f"Loaded ensemble model from {ensemble_filepath}")
        else:
            self.logger.warning(f"Ensemble model file not found: {ensemble_filepath}")
        
        # Load metadata
        metadata_filename = f"{filename_prefix}_metadata.json"
        metadata_filepath = self.models_dir / metadata_filename
        
        if metadata_filepath.exists():
            with open(metadata_filepath, 'r') as f:
                metadata = json.load(f)
            loaded_components['weights'] = metadata.get('weights', {})
            loaded_components['scores'] = metadata.get('scores', {})
            self.logger.info(f"Loaded ensemble metadata from {metadata_filepath}")
        else:
            self.logger.warning(f"Ensemble metadata file not found: {metadata_filepath}")
        
        return loaded_components
    
    def _calculate_metrics(self, y_train: pd.Series, y_pred_train: pd.Series,
                          y_test: pd.Series, y_pred_test: pd.Series) -> Dict[str, float]:
        """
        Calculate performance metrics for the ensemble model.
        
        Args:
            y_train: Training target.
            y_pred_train: Training predictions.
            y_test: Test target.
            y_pred_test: Test predictions.
            
        Returns:
            Dictionary with performance metrics.
        """
        metrics = {
            'train_mae': mean_absolute_error(y_train, y_pred_train),
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
            'train_r2': r2_score(y_train, y_pred_train),
            'test_mae': mean_absolute_error(y_test, y_pred_test),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
            'test_r2': r2_score(y_test, y_pred_test)
        }
        
        # Calculate MAPE
        metrics['train_mape'] = np.mean(np.abs((y_train - y_pred_train) / y_train)) * 100
        metrics['test_mape'] = np.mean(np.abs((y_test - y_pred_test) / y_test)) * 100
        
        # Calculate within 10% and 20% accuracy
        train_within_10 = np.mean(np.abs((y_train - y_pred_train) / y_train) <= 0.1) * 100
        test_within_10 = np.mean(np.abs((y_test - y_pred_test) / y_test) <= 0.1) * 100
        train_within_20 = np.mean(np.abs((y_train - y_pred_train) / y_train) <= 0.2) * 100
        test_within_20 = np.mean(np.abs((y_test - y_pred_test) / y_test) <= 0.2) * 100
        
        metrics.update({
            'train_within_10pct': train_within_10,
            'test_within_10pct': test_within_10,
            'train_within_20pct': train_within_20,
            'test_within_20pct': test_within_20
        })
        
        return metrics


def main():
    """
    Example usage of EnsembleModel.
    """
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize ensemble model
    ensemble = EnsembleModel()
    
    # Example with sample data
    np.random.seed(42)
    n_samples = 1000
    n_features = 10
    
    X_train = pd.DataFrame(np.random.randn(n_samples, n_features))
    y_train = pd.Series(np.random.randn(n_samples))
    X_test = pd.DataFrame(np.random.randn(200, n_features))
    y_test = pd.Series(np.random.randn(200))
    
    # Create sample models (in practice, these would be trained models)
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import RandomForestRegressor
    
    models = {
        'linear': LinearRegression().fit(X_train, y_train),
        'rf': RandomForestRegressor(n_estimators=100, random_state=42).fit(X_train, y_train)
    }
    
    # Train ensemble
    metrics = ensemble.train_ensemble(X_train, y_train, X_test, y_test, models)
    print("Ensemble metrics:", metrics)
    
    # Get ensemble summary
    summary = ensemble.get_ensemble_summary()
    print("Ensemble summary:", summary)
    
    # Save ensemble
    saved_files = ensemble.save_ensemble()
    print("Saved files:", saved_files)


if __name__ == "__main__":
    main()
