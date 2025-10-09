"""
Model evaluation module for rental price prediction.
Handles cross-validation, metrics calculation, and model comparison.
"""

import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Union
from pathlib import Path
import json
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import cross_val_score, StratifiedKFold, KFold
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.metrics import mean_absolute_percentage_error
import warnings
warnings.filterwarnings('ignore')


class ModelEvaluator:
    """
    Model evaluation and comparison utilities.
    
    Attributes:
        logger: Logger instance for tracking operations
        evaluation_results: Dictionary storing evaluation results
        cv_strategy: Cross-validation strategy
    """
    
    def __init__(self, cv_folds: int = 5, random_state: int = 42):
        """
        Initialize ModelEvaluator.
        
        Args:
            cv_folds: Number of cross-validation folds.
            random_state: Random state for reproducibility.
        """
        self.logger = logging.getLogger(__name__)
        self.cv_folds = cv_folds
        self.random_state = random_state
        self.evaluation_results = {}
        
        # Set up cross-validation strategy
        self.cv_strategy = KFold(n_splits=cv_folds, shuffle=True, random_state=random_state)
    
    def calculate_metrics(self, y_true: pd.Series, y_pred: pd.Series) -> Dict[str, float]:
        """
        Calculate comprehensive evaluation metrics.
        
        Args:
            y_true: True values.
            y_pred: Predicted values.
            
        Returns:
            Dictionary with evaluation metrics.
        """
        # Basic metrics
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        r2 = r2_score(y_true, y_pred)
        
        # MAPE (handle division by zero)
        mape = mean_absolute_percentage_error(y_true, y_pred)
        
        # Within percentage accuracy
        within_10pct = np.mean(np.abs((y_true - y_pred) / y_true) <= 0.1) * 100
        within_20pct = np.mean(np.abs((y_true - y_pred) / y_true) <= 0.2) * 100
        
        # Additional metrics
        mse = mean_squared_error(y_true, y_pred)
        mape_manual = np.mean(np.abs((y_true - y_pred) / y_true)) * 100
        
        metrics = {
            'mae': mae,
            'rmse': rmse,
            'mse': mse,
            'r2': r2,
            'mape': mape,
            'mape_manual': mape_manual,
            'within_10pct': within_10pct,
            'within_20pct': within_20pct
        }
        
        return metrics
    
    def cross_validate_model(self, model: Any, X: pd.DataFrame, y: pd.Series,
                           scoring: str = 'neg_mean_absolute_error') -> Dict[str, Any]:
        """
        Perform cross-validation for a model.
        
        Args:
            model: Trained model to evaluate.
            X: Features.
            y: Target.
            scoring: Scoring metric for cross-validation.
            
        Returns:
            Dictionary with cross-validation results.
        """
        self.logger.info(f"Performing {self.cv_folds}-fold cross-validation")
        
        # Perform cross-validation
        cv_scores = cross_val_score(model, X, y, cv=self.cv_strategy, scoring=scoring)
        
        # Calculate statistics
        cv_mean = cv_scores.mean()
        cv_std = cv_scores.std()
        cv_sem = cv_std / np.sqrt(len(cv_scores))
        
        results = {
            'cv_scores': cv_scores.tolist(),
            'cv_mean': cv_mean,
            'cv_std': cv_std,
            'cv_sem': cv_sem,
            'cv_folds': self.cv_folds,
            'scoring': scoring
        }
        
        self.logger.info(f"Cross-validation {scoring}: {cv_mean:.4f} (+/- {cv_std * 2:.4f})")
        
        return results
    
    def evaluate_model(self, model: Any, X_train: pd.DataFrame, y_train: pd.Series,
                      X_test: pd.DataFrame, y_test: pd.Series,
                      model_name: str = 'model') -> Dict[str, Any]:
        """
        Comprehensive evaluation of a model.
        
        Args:
            model: Trained model to evaluate.
            X_train: Training features.
            y_train: Training target.
            X_test: Test features.
            y_test: Test target.
            model_name: Name of the model for identification.
            
        Returns:
            Dictionary with comprehensive evaluation results.
        """
        self.logger.info(f"Evaluating {model_name}")
        
        # Make predictions
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        
        # Calculate metrics for train and test sets
        train_metrics = self.calculate_metrics(y_train, y_pred_train)
        test_metrics = self.calculate_metrics(y_test, y_pred_test)
        
        # Perform cross-validation
        cv_results = self.cross_validate_model(model, X_train, y_train)
        
        # Combine all results
        evaluation_results = {
            'model_name': model_name,
            'train_metrics': train_metrics,
            'test_metrics': test_metrics,
            'cv_results': cv_results,
            'overfitting': {
                'mae_diff': train_metrics['mae'] - test_metrics['mae'],
                'r2_diff': train_metrics['r2'] - test_metrics['r2']
            }
        }
        
        # Store results
        self.evaluation_results[model_name] = evaluation_results
        
        self.logger.info(f"{model_name} - Test R²: {test_metrics['r2']:.4f}, Test MAE: {test_metrics['mae']:.4f}")
        
        return evaluation_results
    
    def compare_models(self, models: Dict[str, Any], X_test: pd.DataFrame, y_test: pd.Series) -> pd.DataFrame:
        """
        Compare performance of multiple models.
        
        Args:
            models: Dictionary mapping model names to trained models.
            X_test: Test features.
            y_test: Test target.
            
        Returns:
            DataFrame with model comparison results.
        """
        self.logger.info("Comparing multiple models")
        
        comparison_results = []
        
        for model_name, model in models.items():
            # Make predictions
            y_pred = model.predict(X_test)
            
            # Calculate metrics
            metrics = self.calculate_metrics(y_test, y_pred)
            
            # Add model name
            metrics['model_name'] = model_name
            
            comparison_results.append(metrics)
        
        # Create comparison DataFrame
        comparison_df = pd.DataFrame(comparison_results)
        
        # Sort by R² score (descending)
        comparison_df = comparison_df.sort_values('r2', ascending=False)
        
        self.logger.info("Model comparison completed")
        return comparison_df
    
    def create_evaluation_report(self, models: Dict[str, Any], X_test: pd.DataFrame, y_test: pd.Series,
                               save_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Create comprehensive evaluation report.
        
        Args:
            models: Dictionary mapping model names to trained models.
            X_test: Test features.
            y_test: Test target.
            save_path: Path to save the report. If None, doesn't save.
            
        Returns:
            Dictionary with evaluation report.
        """
        self.logger.info("Creating evaluation report")
        
        # Compare models
        comparison_df = self.compare_models(models, X_test, y_test)
        
        # Get best model
        best_model_name = comparison_df.iloc[0]['model_name']
        best_model = models[best_model_name]
        
        # Detailed evaluation of best model
        best_model_evaluation = self.evaluate_model(best_model, X_test, y_test, X_test, y_test, best_model_name)
        
        # Create report
        report = {
            'summary': {
                'total_models': len(models),
                'best_model': best_model_name,
                'best_r2': comparison_df.iloc[0]['r2'],
                'best_mae': comparison_df.iloc[0]['mae']
            },
            'model_comparison': comparison_df.to_dict('records'),
            'best_model_details': best_model_evaluation,
            'recommendations': self._generate_recommendations(comparison_df)
        }
        
        # Save report if path provided
        if save_path:
            with open(save_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            self.logger.info(f"Evaluation report saved to {save_path}")
        
        return report
    
    def plot_model_comparison(self, comparison_df: pd.DataFrame, 
                            metrics: List[str] = ['mae', 'rmse', 'r2'],
                            save_path: Optional[Path] = None) -> None:
        """
        Create visualization of model comparison.
        
        Args:
            comparison_df: DataFrame with model comparison results.
            metrics: List of metrics to plot.
            save_path: Path to save the plot. If None, doesn't save.
        """
        self.logger.info("Creating model comparison visualization")
        
        # Set up the plot
        fig, axes = plt.subplots(1, len(metrics), figsize=(5 * len(metrics), 6))
        if len(metrics) == 1:
            axes = [axes]
        
        for i, metric in enumerate(metrics):
            if metric in comparison_df.columns:
                # Create bar plot
                axes[i].bar(comparison_df['model_name'], comparison_df[metric])
                axes[i].set_title(f'Model Comparison - {metric.upper()}')
                axes[i].set_xlabel('Model')
                axes[i].set_ylabel(metric.upper())
                axes[i].tick_params(axis='x', rotation=45)
                
                # Add value labels on bars
                for j, v in enumerate(comparison_df[metric]):
                    axes[i].text(j, v, f'{v:.3f}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Model comparison plot saved to {save_path}")
        
        plt.show()
    
    def plot_prediction_analysis(self, y_true: pd.Series, y_pred: pd.Series,
                                model_name: str = 'Model', save_path: Optional[Path] = None) -> None:
        """
        Create comprehensive prediction analysis plots.
        
        Args:
            y_true: True values.
            y_pred: Predicted values.
            model_name: Name of the model for the plot title.
            save_path: Path to save the plot. If None, doesn't save.
        """
        self.logger.info(f"Creating prediction analysis for {model_name}")
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Scatter plot: True vs Predicted
        axes[0, 0].scatter(y_true, y_pred, alpha=0.6)
        axes[0, 0].plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
        axes[0, 0].set_xlabel('True Values')
        axes[0, 0].set_ylabel('Predicted Values')
        axes[0, 0].set_title(f'{model_name} - True vs Predicted')
        
        # Add R² to the plot
        r2 = r2_score(y_true, y_pred)
        axes[0, 0].text(0.05, 0.95, f'R² = {r2:.3f}', transform=axes[0, 0].transAxes, 
                        bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # 2. Residuals plot
        residuals = y_true - y_pred
        axes[0, 1].scatter(y_pred, residuals, alpha=0.6)
        axes[0, 1].axhline(y=0, color='r', linestyle='--')
        axes[0, 1].set_xlabel('Predicted Values')
        axes[0, 1].set_ylabel('Residuals')
        axes[0, 1].set_title(f'{model_name} - Residuals Plot')
        
        # 3. Residuals histogram
        axes[1, 0].hist(residuals, bins=30, alpha=0.7, edgecolor='black')
        axes[1, 0].set_xlabel('Residuals')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].set_title(f'{model_name} - Residuals Distribution')
        
        # 4. Q-Q plot for residuals
        from scipy import stats
        stats.probplot(residuals, dist="norm", plot=axes[1, 1])
        axes[1, 1].set_title(f'{model_name} - Q-Q Plot of Residuals')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Prediction analysis plot saved to {save_path}")
        
        plt.show()
    
    def _generate_recommendations(self, comparison_df: pd.DataFrame) -> List[str]:
        """
        Generate recommendations based on model comparison.
        
        Args:
            comparison_df: DataFrame with model comparison results.
            
        Returns:
            List of recommendation strings.
        """
        recommendations = []
        
        # Best model recommendation
        best_model = comparison_df.iloc[0]
        recommendations.append(f"Best performing model: {best_model['model_name']} (R² = {best_model['r2']:.3f})")
        
        # Overfitting check
        if 'train_metrics' in comparison_df.columns and 'test_metrics' in comparison_df.columns:
            # This would need to be implemented based on available data
            pass
        
        # Performance gaps
        r2_range = comparison_df['r2'].max() - comparison_df['r2'].min()
        if r2_range > 0.1:
            recommendations.append("Significant performance gap between models. Consider ensemble methods.")
        
        # MAE analysis
        mae_range = comparison_df['mae'].max() - comparison_df['mae'].min()
        if mae_range > 50:  # Assuming price in BRL
            recommendations.append("Large variation in MAE between models. Review feature engineering.")
        
        return recommendations
    
    def save_evaluation_results(self, save_path: Path) -> None:
        """
        Save evaluation results to file.
        
        Args:
            save_path: Path to save the results.
        """
        with open(save_path, 'w') as f:
            json.dump(self.evaluation_results, f, indent=2, default=str)
        
        self.logger.info(f"Evaluation results saved to {save_path}")


def main():
    """
    Example usage of ModelEvaluator.
    """
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize evaluator
    evaluator = ModelEvaluator()
    
    # Example with sample data
    np.random.seed(42)
    n_samples = 1000
    n_features = 10
    
    X_train = pd.DataFrame(np.random.randn(n_samples, n_features))
    y_train = pd.Series(np.random.randn(n_samples))
    X_test = pd.DataFrame(np.random.randn(200, n_features))
    y_test = pd.Series(np.random.randn(200))
    
    # Create sample models
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import RandomForestRegressor
    
    models = {
        'linear': LinearRegression().fit(X_train, y_train),
        'rf': RandomForestRegressor(n_estimators=100, random_state=42).fit(X_train, y_train)
    }
    
    # Evaluate models
    for name, model in models.items():
        evaluation = evaluator.evaluate_model(model, X_train, y_train, X_test, y_test, name)
        print(f"{name} evaluation:", evaluation['test_metrics'])
    
    # Compare models
    comparison = evaluator.compare_models(models, X_test, y_test)
    print("Model comparison:", comparison)
    
    # Create evaluation report
    report = evaluator.create_evaluation_report(models, X_test, y_test)
    print("Evaluation report:", report['summary'])


if __name__ == "__main__":
    main()
