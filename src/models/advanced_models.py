"""
Advanced machine learning models for rental price prediction.
Implements XGBoost, LightGBM, and CatBoost models.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import pickle
import json

# Advanced ML libraries
import xgboost as xgb
import lightgbm as lgb
import catboost as cb

from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from config import ADVANCED_MODELS, MODELS_DIR, RANDOM_STATE


class AdvancedModels:
    """
    Advanced machine learning models for rental price prediction.
    
    Attributes:
        logger: Logger instance for tracking operations
        models_dir: Path to models directory
        trained_models: Dictionary storing trained models
        model_scores: Dictionary storing model performance scores
    """
    
    def __init__(self, models_dir: Optional[Path] = None):
        """
        Initialize AdvancedModels.
        
        Args:
            models_dir: Path to models directory. If None, uses config default.
        """
        self.logger = logging.getLogger(__name__)
        self.models_dir = models_dir or MODELS_DIR
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.trained_models = {}
        self.model_scores = {}
    
    def train_xgboost(self, X_train: pd.DataFrame, y_train: pd.Series,
                      X_test: pd.DataFrame, y_test: pd.Series,
                      params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Train XGBoost model.
        
        Args:
            X_train: Training features.
            y_train: Training target.
            X_test: Test features.
            y_test: Test target.
            params: Model parameters. If None, uses config default.
            
        Returns:
            Dictionary with model performance metrics.
        """
        self.logger.info("Training XGBoost model")
        
        if params is None:
            params = ADVANCED_MODELS['xgboost']
        
        # Initialize model
        model = xgb.XGBRegressor(**params)
        
        # Train model
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        # Calculate metrics
        metrics = self._calculate_metrics(y_train, y_pred_train, y_test, y_pred_test)
        
        # Store model and metrics
        self.trained_models['xgboost'] = model
        self.model_scores['xgboost'] = metrics
        
        self.logger.info(f"XGBoost - Test R²: {metrics['test_r2']:.4f}, Test MAE: {metrics['test_mae']:.4f}")
        
        return metrics
    
    def train_lightgbm(self, X_train: pd.DataFrame, y_train: pd.Series,
                       X_test: pd.DataFrame, y_test: pd.Series,
                       params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Train LightGBM model.
        
        Args:
            X_train: Training features.
            y_train: Training target.
            X_test: Test features.
            y_test: Test target.
            params: Model parameters. If None, uses config default.
            
        Returns:
            Dictionary with model performance metrics.
        """
        self.logger.info("Training LightGBM model")
        
        if params is None:
            params = ADVANCED_MODELS['lightgbm']
        
        # Initialize model
        model = lgb.LGBMRegressor(**params)
        
        # Train model
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        # Calculate metrics
        metrics = self._calculate_metrics(y_train, y_pred_train, y_test, y_pred_test)
        
        # Store model and metrics
        self.trained_models['lightgbm'] = model
        self.model_scores['lightgbm'] = metrics
        
        self.logger.info(f"LightGBM - Test R²: {metrics['test_r2']:.4f}, Test MAE: {metrics['test_mae']:.4f}")
        
        return metrics
    
    def train_catboost(self, X_train: pd.DataFrame, y_train: pd.Series,
                       X_test: pd.DataFrame, y_test: pd.Series,
                       params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Train CatBoost model.
        
        Args:
            X_train: Training features.
            y_train: Training target.
            X_test: Test features.
            y_test: Test target.
            params: Model parameters. If None, uses config default.
            
        Returns:
            Dictionary with model performance metrics.
        """
        self.logger.info("Training CatBoost model")
        
        if params is None:
            params = ADVANCED_MODELS['catboost']
        
        # Initialize model
        model = cb.CatBoostRegressor(**params)
        
        # Train model
        model.fit(X_train, y_train)
        
        # Make predictions
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        # Calculate metrics
        metrics = self._calculate_metrics(y_train, y_pred_train, y_test, y_pred_test)
        
        # Store model and metrics
        self.trained_models['catboost'] = model
        self.model_scores['catboost'] = metrics
        
        self.logger.info(f"CatBoost - Test R²: {metrics['test_r2']:.4f}, Test MAE: {metrics['test_mae']:.4f}")
        
        return metrics
    
    def train_all_advanced_models(self, X_train: pd.DataFrame, y_train: pd.Series,
                                 X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Dict[str, Any]]:
        """
        Train all advanced models.
        
        Args:
            X_train: Training features.
            y_train: Training target.
            X_test: Test features.
            y_test: Test target.
            
        Returns:
            Dictionary mapping model names to performance metrics.
        """
        self.logger.info("Training all advanced models")
        
        all_metrics = {}
        
        # Train XGBoost
        try:
            xgb_metrics = self.train_xgboost(X_train, y_train, X_test, y_test)
            all_metrics['xgboost'] = xgb_metrics
        except Exception as e:
            self.logger.error(f"Failed to train XGBoost: {e}")
            all_metrics['xgboost'] = {'error': str(e)}
        
        # Train LightGBM
        try:
            lgb_metrics = self.train_lightgbm(X_train, y_train, X_test, y_test)
            all_metrics['lightgbm'] = lgb_metrics
        except Exception as e:
            self.logger.error(f"Failed to train LightGBM: {e}")
            all_metrics['lightgbm'] = {'error': str(e)}
        
        # Train CatBoost
        try:
            cb_metrics = self.train_catboost(X_train, y_train, X_test, y_test)
            all_metrics['catboost'] = cb_metrics
        except Exception as e:
            self.logger.error(f"Failed to train CatBoost: {e}")
            all_metrics['catboost'] = {'error': str(e)}
        
        self.logger.info("All advanced models trained")
        return all_metrics
    
    def hyperparameter_tuning(self, X_train: pd.DataFrame, y_train: pd.Series,
                             model_name: str, param_grid: Dict[str, List[Any]],
                             cv_folds: int = 5) -> Dict[str, Any]:
        """
        Perform hyperparameter tuning for a specific model.
        
        Args:
            X_train: Training features.
            y_train: Training target.
            model_name: Name of the model to tune.
            param_grid: Parameter grid for tuning.
            cv_folds: Number of cross-validation folds.
            
        Returns:
            Dictionary with best parameters and scores.
        """
        self.logger.info(f"Performing hyperparameter tuning for {model_name}")
        
        # Get base model
        if model_name == 'xgboost':
            base_model = xgb.XGBRegressor(random_state=RANDOM_STATE)
        elif model_name == 'lightgbm':
            base_model = lgb.LGBMRegressor(random_state=RANDOM_STATE, verbose=-1)
        elif model_name == 'catboost':
            base_model = cb.CatBoostRegressor(random_seed=RANDOM_STATE, verbose=False)
        else:
            raise ValueError(f"Unknown model: {model_name}")
        
        # Perform grid search
        grid_search = GridSearchCV(
            base_model, param_grid, cv=cv_folds,
            scoring='neg_mean_absolute_error', n_jobs=-1
        )
        
        grid_search.fit(X_train, y_train)
        
        # Store best model
        self.trained_models[f'{model_name}_tuned'] = grid_search.best_estimator_
        
        results = {
            'best_params': grid_search.best_params_,
            'best_score': grid_search.best_score_,
            'cv_results': grid_search.cv_results_
        }
        
        self.logger.info(f"Best parameters for {model_name}: {grid_search.best_params_}")
        return results
    
    def cross_validate_model(self, X: pd.DataFrame, y: pd.Series,
                           model_name: str, cv_folds: int = 5) -> Dict[str, Any]:
        """
        Perform cross-validation for a specific model.
        
        Args:
            X: Features.
            y: Target.
            model_name: Name of the model to validate.
            cv_folds: Number of cross-validation folds.
            
        Returns:
            Dictionary with cross-validation results.
        """
        self.logger.info(f"Performing cross-validation for {model_name}")
        
        # Get model
        if model_name not in self.trained_models:
            raise ValueError(f"Model {model_name} not found. Train it first.")
        
        model = self.trained_models[model_name]
        
        # Perform cross-validation
        cv_scores = cross_val_score(model, X, y, cv=cv_folds, scoring='neg_mean_absolute_error')
        
        results = {
            'cv_scores': cv_scores,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'cv_folds': cv_folds
        }
        
        self.logger.info(f"Cross-validation MAE: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
        return results
    
    def get_feature_importance(self, model_name: str, feature_names: List[str]) -> pd.DataFrame:
        """
        Get feature importance for a specific model.
        
        Args:
            model_name: Name of the model.
            feature_names: List of feature names.
            
        Returns:
            DataFrame with feature importance.
        """
        if model_name not in self.trained_models:
            raise ValueError(f"Model {model_name} not found. Train it first.")
        
        model = self.trained_models[model_name]
        
        # Get feature importance
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
        else:
            raise ValueError(f"Model {model_name} does not support feature importance")
        
        # Create DataFrame
        importance_df = pd.DataFrame({
            'feature': feature_names,
            'importance': importance
        }).sort_values('importance', ascending=False)
        
        return importance_df
    
    def get_shap_values(self, model_name: str, X: pd.DataFrame, feature_names: List[str]) -> np.ndarray:
        """
        Get SHAP values for model interpretation.
        
        Args:
            model_name: Name of the model.
            X: Features to explain.
            feature_names: List of feature names.
            
        Returns:
            SHAP values array.
        """
        try:
            import shap
        except ImportError:
            self.logger.warning("SHAP not available. Install with: pip install shap")
            return None
        
        if model_name not in self.trained_models:
            raise ValueError(f"Model {model_name} not found. Train it first.")
        
        model = self.trained_models[model_name]
        
        # Create SHAP explainer
        if model_name == 'xgboost':
            explainer = shap.TreeExplainer(model)
        elif model_name == 'lightgbm':
            explainer = shap.TreeExplainer(model)
        elif model_name == 'catboost':
            explainer = shap.TreeExplainer(model)
        else:
            raise ValueError(f"SHAP not supported for {model_name}")
        
        # Calculate SHAP values
        shap_values = explainer.shap_values(X)
        
        return shap_values
    
    def save_models(self, filename_prefix: str = 'advanced') -> Dict[str, Path]:
        """
        Save trained models to files.
        
        Args:
            filename_prefix: Prefix for saved files.
            
        Returns:
            Dictionary mapping model names to file paths.
        """
        saved_files = {}
        
        for model_name, model in self.trained_models.items():
            filename = f"{filename_prefix}_{model_name}.pkl"
            filepath = self.models_dir / filename
            
            with open(filepath, 'wb') as f:
                pickle.dump(model, f)
            
            saved_files[model_name] = filepath
            self.logger.info(f"Saved {model_name} model to {filepath}")
        
        # Save model scores
        scores_filename = f"{filename_prefix}_scores.json"
        scores_filepath = self.models_dir / scores_filename
        
        with open(scores_filepath, 'w') as f:
            json.dump(self.model_scores, f, indent=2, default=str)
        
        saved_files['scores'] = scores_filepath
        self.logger.info(f"Saved model scores to {scores_filepath}")
        
        return saved_files
    
    def load_models(self, filename_prefix: str = 'advanced') -> Dict[str, Any]:
        """
        Load trained models from files.
        
        Args:
            filename_prefix: Prefix for saved files.
            
        Returns:
            Dictionary mapping model names to loaded models.
        """
        loaded_models = {}
        
        # Load model files
        for model_name in ['xgboost', 'lightgbm', 'catboost']:
            filename = f"{filename_prefix}_{model_name}.pkl"
            filepath = self.models_dir / filename
            
            if filepath.exists():
                with open(filepath, 'rb') as f:
                    loaded_models[model_name] = pickle.load(f)
                self.logger.info(f"Loaded {model_name} model from {filepath}")
            else:
                self.logger.warning(f"Model file not found: {filepath}")
        
        # Load scores
        scores_filename = f"{filename_prefix}_scores.json"
        scores_filepath = self.models_dir / scores_filename
        
        if scores_filepath.exists():
            with open(scores_filepath, 'r') as f:
                loaded_scores = json.load(f)
            loaded_models['scores'] = loaded_scores
            self.logger.info(f"Loaded model scores from {scores_filepath}")
        
        return loaded_models
    
    def _calculate_metrics(self, y_train: pd.Series, y_pred_train: pd.Series,
                          y_test: pd.Series, y_pred_test: pd.Series) -> Dict[str, float]:
        """
        Calculate performance metrics for a model.
        
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
    Example usage of AdvancedModels.
    """
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize advanced models
    advanced = AdvancedModels()
    
    # Example with sample data
    np.random.seed(42)
    n_samples = 1000
    n_features = 10
    
    X_train = pd.DataFrame(np.random.randn(n_samples, n_features))
    y_train = pd.Series(np.random.randn(n_samples))
    X_test = pd.DataFrame(np.random.randn(200, n_features))
    y_test = pd.Series(np.random.randn(200))
    
    # Train all advanced models
    metrics = advanced.train_all_advanced_models(X_train, y_train, X_test, y_test)
    print("Advanced model metrics:", metrics)
    
    # Get feature importance for XGBoost
    feature_names = [f'feature_{i}' for i in range(n_features)]
    importance = advanced.get_feature_importance('xgboost', feature_names)
    print("Feature importance:", importance.head())
    
    # Save models
    saved_files = advanced.save_models()
    print("Saved files:", saved_files)


if __name__ == "__main__":
    main()
