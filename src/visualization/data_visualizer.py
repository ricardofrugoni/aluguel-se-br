"""
Data visualization module for rental price prediction.
Creates charts and plots for data analysis and model evaluation.
"""

import logging
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

from config import REPORTS_DIR


class DataVisualizer:
    """
    Creates data visualizations for rental price analysis.
    
    Attributes:
        logger: Logger instance for tracking operations
        reports_dir: Path to reports directory
        style_config: Matplotlib style configuration
    """
    
    def __init__(self, reports_dir: Optional[Path] = None):
        """
        Initialize DataVisualizer.
        
        Args:
            reports_dir: Path to reports directory. If None, uses config default.
        """
        self.logger = logging.getLogger(__name__)
        self.reports_dir = reports_dir or REPORTS_DIR
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # Set up plotting style
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Configure matplotlib
        plt.rcParams['figure.figsize'] = (12, 8)
        plt.rcParams['font.size'] = 10
        plt.rcParams['axes.titlesize'] = 14
        plt.rcParams['axes.labelsize'] = 12
        plt.rcParams['xtick.labelsize'] = 10
        plt.rcParams['ytick.labelsize'] = 10
        plt.rcParams['legend.fontsize'] = 10
    
    def plot_price_distribution(self, df: pd.DataFrame, price_col: str = 'price',
                               title: str = 'Price Distribution') -> plt.Figure:
        """
        Create price distribution plots.
        
        Args:
            df: DataFrame with price data.
            price_col: Name of price column.
            title: Title for the plot.
            
        Returns:
            Matplotlib figure object.
        """
        self.logger.info("Creating price distribution plot")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(title, fontsize=16)
        
        # 1. Histogram
        axes[0, 0].hist(df[price_col], bins=50, alpha=0.7, edgecolor='black')
        axes[0, 0].set_xlabel('Price (BRL)')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].set_title('Price Histogram')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Box plot
        axes[0, 1].boxplot(df[price_col])
        axes[0, 1].set_ylabel('Price (BRL)')
        axes[0, 1].set_title('Price Box Plot')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Log-transformed histogram
        log_prices = np.log1p(df[price_col])
        axes[1, 0].hist(log_prices, bins=50, alpha=0.7, edgecolor='black')
        axes[1, 0].set_xlabel('Log(Price + 1)')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].set_title('Log-Transformed Price Distribution')
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Q-Q plot
        from scipy import stats
        stats.probplot(df[price_col], dist="norm", plot=axes[1, 1])
        axes[1, 1].set_title('Q-Q Plot of Prices')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        return fig
    
    def plot_feature_distributions(self, df: pd.DataFrame, 
                                 numeric_cols: List[str] = None,
                                 title: str = 'Feature Distributions') -> plt.Figure:
        """
        Create distribution plots for numeric features.
        
        Args:
            df: DataFrame with feature data.
            numeric_cols: List of numeric columns to plot. If None, auto-detect.
            title: Title for the plot.
            
        Returns:
            Matplotlib figure object.
        """
        self.logger.info("Creating feature distribution plots")
        
        if numeric_cols is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Calculate subplot dimensions
        n_cols = 3
        n_rows = (len(numeric_cols) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))
        fig.suptitle(title, fontsize=16)
        
        if n_rows == 1:
            axes = axes.reshape(1, -1)
        
        for i, col in enumerate(numeric_cols):
            row = i // n_cols
            col_idx = i % n_cols
            
            if n_rows == 1:
                ax = axes[col_idx]
            else:
                ax = axes[row, col_idx]
            
            # Create histogram
            ax.hist(df[col].dropna(), bins=30, alpha=0.7, edgecolor='black')
            ax.set_xlabel(col)
            ax.set_ylabel('Frequency')
            ax.set_title(f'Distribution of {col}')
            ax.grid(True, alpha=0.3)
        
        # Hide empty subplots
        for i in range(len(numeric_cols), n_rows * n_cols):
            row = i // n_cols
            col_idx = i % n_cols
            if n_rows == 1:
                axes[col_idx].set_visible(False)
            else:
                axes[row, col_idx].set_visible(False)
        
        plt.tight_layout()
        return fig
    
    def plot_correlation_matrix(self, df: pd.DataFrame, 
                              numeric_cols: List[str] = None,
                              title: str = 'Feature Correlation Matrix') -> plt.Figure:
        """
        Create correlation matrix heatmap.
        
        Args:
            df: DataFrame with feature data.
            numeric_cols: List of numeric columns to include. If None, auto-detect.
            title: Title for the plot.
            
        Returns:
            Matplotlib figure object.
        """
        self.logger.info("Creating correlation matrix")
        
        if numeric_cols is None:
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Calculate correlation matrix
        corr_matrix = df[numeric_cols].corr()
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(12, 10))
        
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
        sns.heatmap(corr_matrix, mask=mask, annot=True, cmap='coolwarm', center=0,
                   square=True, linewidths=0.5, cbar_kws={"shrink": 0.8})
        
        ax.set_title(title, fontsize=16)
        plt.tight_layout()
        return fig
    
    def plot_price_vs_features(self, df: pd.DataFrame, price_col: str = 'price',
                             feature_cols: List[str] = None,
                             title: str = 'Price vs Features') -> plt.Figure:
        """
        Create scatter plots of price vs other features.
        
        Args:
            df: DataFrame with data.
            price_col: Name of price column.
            feature_cols: List of feature columns to plot. If None, auto-detect.
            title: Title for the plot.
            
        Returns:
            Matplotlib figure object.
        """
        self.logger.info("Creating price vs features plots")
        
        if feature_cols is None:
            feature_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            feature_cols = [col for col in feature_cols if col != price_col]
        
        # Limit to top 6 features for readability
        feature_cols = feature_cols[:6]
        
        n_cols = 3
        n_rows = (len(feature_cols) + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))
        fig.suptitle(title, fontsize=16)
        
        if n_rows == 1:
            axes = axes.reshape(1, -1)
        
        for i, col in enumerate(feature_cols):
            row = i // n_cols
            col_idx = i % n_cols
            
            if n_rows == 1:
                ax = axes[col_idx]
            else:
                ax = axes[row, col_idx]
            
            # Create scatter plot
            ax.scatter(df[col], df[price_col], alpha=0.6, s=20)
            ax.set_xlabel(col)
            ax.set_ylabel('Price (BRL)')
            ax.set_title(f'Price vs {col}')
            ax.grid(True, alpha=0.3)
            
            # Add trend line
            z = np.polyfit(df[col].dropna(), df[price_col].dropna(), 1)
            p = np.poly1d(z)
            ax.plot(df[col], p(df[col]), "r--", alpha=0.8)
        
        # Hide empty subplots
        for i in range(len(feature_cols), n_rows * n_cols):
            row = i // n_cols
            col_idx = i % n_cols
            if n_rows == 1:
                axes[col_idx].set_visible(False)
            else:
                axes[row, col_idx].set_visible(False)
        
        plt.tight_layout()
        return fig
    
    def plot_model_performance(self, model_results: Dict[str, Dict[str, float]],
                             title: str = 'Model Performance Comparison') -> plt.Figure:
        """
        Create model performance comparison plots.
        
        Args:
            model_results: Dictionary mapping model names to performance metrics.
            title: Title for the plot.
            
        Returns:
            Matplotlib figure object.
        """
        self.logger.info("Creating model performance plots")
        
        # Extract metrics
        models = list(model_results.keys())
        metrics = ['mae', 'rmse', 'r2', 'mape']
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(title, fontsize=16)
        
        for i, metric in enumerate(metrics):
            row = i // 2
            col = i % 2
            
            # Extract metric values
            values = [model_results[model].get(metric, 0) for model in models]
            
            # Create bar plot
            bars = axes[row, col].bar(models, values, alpha=0.7)
            axes[row, col].set_title(f'{metric.upper()} Comparison')
            axes[row, col].set_ylabel(metric.upper())
            axes[row, col].tick_params(axis='x', rotation=45)
            axes[row, col].grid(True, alpha=0.3)
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                axes[row, col].text(bar.get_x() + bar.get_width()/2., height,
                                  f'{value:.3f}', ha='center', va='bottom')
        
        plt.tight_layout()
        return fig
    
    def plot_feature_importance(self, importance_df: pd.DataFrame,
                               title: str = 'Feature Importance',
                               top_n: int = 20) -> plt.Figure:
        """
        Create feature importance plot.
        
        Args:
            importance_df: DataFrame with feature importance data.
            title: Title for the plot.
            top_n: Number of top features to show.
            
        Returns:
            Matplotlib figure object.
        """
        self.logger.info("Creating feature importance plot")
        
        # Get top N features
        top_features = importance_df.head(top_n)
        
        # Create horizontal bar plot
        fig, ax = plt.subplots(figsize=(10, 8))
        
        bars = ax.barh(range(len(top_features)), top_features['importance'])
        ax.set_yticks(range(len(top_features)))
        ax.set_yticklabels(top_features['feature'])
        ax.set_xlabel('Importance')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)
        
        # Add value labels
        for i, (bar, value) in enumerate(zip(bars, top_features['importance'])):
            ax.text(bar.get_width() + 0.01, bar.get_y() + bar.get_height()/2,
                   f'{value:.3f}', ha='left', va='center')
        
        plt.tight_layout()
        return fig
    
    def plot_prediction_analysis(self, y_true: pd.Series, y_pred: pd.Series,
                                model_name: str = 'Model') -> plt.Figure:
        """
        Create comprehensive prediction analysis plots.
        
        Args:
            y_true: True values.
            y_pred: Predicted values.
            model_name: Name of the model for the plot title.
            
        Returns:
            Matplotlib figure object.
        """
        self.logger.info(f"Creating prediction analysis for {model_name}")
        
        # Calculate metrics
        mae = np.mean(np.abs(y_true - y_pred))
        rmse = np.sqrt(np.mean((y_true - y_pred) ** 2))
        r2 = 1 - np.sum((y_true - y_pred) ** 2) / np.sum((y_true - np.mean(y_true)) ** 2)
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'{model_name} - Prediction Analysis', fontsize=16)
        
        # 1. Scatter plot: True vs Predicted
        axes[0, 0].scatter(y_true, y_pred, alpha=0.6)
        axes[0, 0].plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
        axes[0, 0].set_xlabel('True Values')
        axes[0, 0].set_ylabel('Predicted Values')
        axes[0, 0].set_title('True vs Predicted')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Add R² to the plot
        axes[0, 0].text(0.05, 0.95, f'R² = {r2:.3f}', transform=axes[0, 0].transAxes,
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        # 2. Residuals plot
        residuals = y_true - y_pred
        axes[0, 1].scatter(y_pred, residuals, alpha=0.6)
        axes[0, 1].axhline(y=0, color='r', linestyle='--')
        axes[0, 1].set_xlabel('Predicted Values')
        axes[0, 1].set_ylabel('Residuals')
        axes[0, 1].set_title('Residuals Plot')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. Residuals histogram
        axes[1, 0].hist(residuals, bins=30, alpha=0.7, edgecolor='black')
        axes[1, 0].set_xlabel('Residuals')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].set_title('Residuals Distribution')
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Q-Q plot for residuals
        from scipy import stats
        stats.probplot(residuals, dist="norm", plot=axes[1, 1])
        axes[1, 1].set_title('Q-Q Plot of Residuals')
        axes[1, 1].grid(True, alpha=0.3)
        
        # Add metrics text
        metrics_text = f'MAE: {mae:.2f}\nRMSE: {rmse:.2f}\nR²: {r2:.3f}'
        axes[1, 1].text(0.05, 0.95, metrics_text, transform=axes[1, 1].transAxes,
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        return fig
    
    def plot_geospatial_analysis(self, df: pd.DataFrame, 
                               lat_col: str = 'latitude', lon_col: str = 'longitude',
                               price_col: str = 'price',
                               title: str = 'Geospatial Price Analysis') -> plt.Figure:
        """
        Create geospatial analysis plots.
        
        Args:
            df: DataFrame with geospatial data.
            lat_col: Name of latitude column.
            lon_col: Name of longitude column.
            price_col: Name of price column.
            title: Title for the plot.
            
        Returns:
            Matplotlib figure object.
        """
        self.logger.info("Creating geospatial analysis plots")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(title, fontsize=16)
        
        # 1. Scatter plot: Latitude vs Price
        axes[0, 0].scatter(df[lat_col], df[price_col], alpha=0.6, s=20)
        axes[0, 0].set_xlabel('Latitude')
        axes[0, 0].set_ylabel('Price (BRL)')
        axes[0, 0].set_title('Price vs Latitude')
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. Scatter plot: Longitude vs Price
        axes[0, 1].scatter(df[lon_col], df[price_col], alpha=0.6, s=20)
        axes[0, 1].set_xlabel('Longitude')
        axes[0, 1].set_ylabel('Price (BRL)')
        axes[0, 1].set_title('Price vs Longitude')
        axes[0, 1].grid(True, alpha=0.3)
        
        # 3. 2D histogram: Latitude vs Longitude
        axes[1, 0].hist2d(df[lon_col], df[lat_col], bins=50, alpha=0.7)
        axes[1, 0].set_xlabel('Longitude')
        axes[1, 0].set_ylabel('Latitude')
        axes[1, 0].set_title('Property Density Map')
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Price heatmap
        # Create grid for heatmap
        lat_bins = np.linspace(df[lat_col].min(), df[lat_col].max(), 20)
        lon_bins = np.linspace(df[lon_col].min(), df[lon_col].max(), 20)
        
        # Calculate average price in each grid cell
        grid_prices = np.zeros((len(lat_bins)-1, len(lon_bins)-1))
        for i in range(len(lat_bins)-1):
            for j in range(len(lon_bins)-1):
                mask = ((df[lat_col] >= lat_bins[i]) & (df[lat_col] < lat_bins[i+1]) &
                       (df[lon_col] >= lon_bins[j]) & (df[lon_col] < lon_bins[j+1]))
                if mask.any():
                    grid_prices[i, j] = df[mask][price_col].mean()
        
        im = axes[1, 1].imshow(grid_prices, extent=[df[lon_col].min(), df[lon_col].max(),
                                                   df[lat_col].min(), df[lat_col].max()],
                              aspect='auto', origin='lower', cmap='viridis')
        axes[1, 1].set_xlabel('Longitude')
        axes[1, 1].set_ylabel('Latitude')
        axes[1, 1].set_title('Average Price Heatmap')
        plt.colorbar(im, ax=axes[1, 1], label='Average Price (BRL)')
        
        plt.tight_layout()
        return fig
    
    def save_plot(self, fig: plt.Figure, filename: str, dpi: int = 300) -> Path:
        """
        Save plot to file.
        
        Args:
            fig: Matplotlib figure object to save.
            filename: Name of the file to save.
            dpi: Resolution for saved image.
            
        Returns:
            Path to saved file.
        """
        filepath = self.reports_dir / filename
        
        fig.savefig(filepath, dpi=dpi, bbox_inches='tight')
        self.logger.info(f"Plot saved to {filepath}")
        
        return filepath
    
    def create_comprehensive_report(self, df: pd.DataFrame, model_results: Dict[str, Dict[str, float]],
                                  importance_df: pd.DataFrame, y_true: pd.Series, y_pred: pd.Series,
                                  model_name: str = 'Model') -> List[plt.Figure]:
        """
        Create comprehensive visualization report.
        
        Args:
            df: DataFrame with data.
            model_results: Dictionary with model performance results.
            importance_df: DataFrame with feature importance.
            y_true: True values.
            y_pred: Predicted values.
            model_name: Name of the model.
            
        Returns:
            List of matplotlib figure objects.
        """
        self.logger.info("Creating comprehensive visualization report")
        
        figures = []
        
        # 1. Price distribution
        fig1 = self.plot_price_distribution(df)
        figures.append(fig1)
        
        # 2. Feature distributions
        fig2 = self.plot_feature_distributions(df)
        figures.append(fig2)
        
        # 3. Correlation matrix
        fig3 = self.plot_correlation_matrix(df)
        figures.append(fig3)
        
        # 4. Price vs features
        fig4 = self.plot_price_vs_features(df)
        figures.append(fig4)
        
        # 5. Model performance
        fig5 = self.plot_model_performance(model_results)
        figures.append(fig5)
        
        # 6. Feature importance
        fig6 = self.plot_feature_importance(importance_df)
        figures.append(fig6)
        
        # 7. Prediction analysis
        fig7 = self.plot_prediction_analysis(y_true, y_pred, model_name)
        figures.append(fig7)
        
        # 8. Geospatial analysis
        fig8 = self.plot_geospatial_analysis(df)
        figures.append(fig8)
        
        self.logger.info(f"Created {len(figures)} visualization plots")
        return figures


def main():
    """
    Example usage of DataVisualizer.
    """
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize data visualizer
    visualizer = DataVisualizer()
    
    # Example with sample data
    np.random.seed(42)
    n_samples = 1000
    
    sample_data = pd.DataFrame({
        'latitude': np.random.uniform(-23.8, -23.4, n_samples),
        'longitude': np.random.uniform(-46.8, -46.4, n_samples),
        'price': np.random.lognormal(5, 0.5, n_samples),
        'bedrooms': np.random.randint(1, 5, n_samples),
        'bathrooms': np.random.randint(1, 3, n_samples)
    })
    
    # Create price distribution plot
    fig1 = visualizer.plot_price_distribution(sample_data)
    print("Price distribution plot created")
    
    # Create feature distributions plot
    fig2 = visualizer.plot_feature_distributions(sample_data)
    print("Feature distributions plot created")
    
    # Save plots
    visualizer.save_plot(fig1, 'price_distribution.png')
    visualizer.save_plot(fig2, 'feature_distributions.png')
    print("Plots saved successfully")


if __name__ == "__main__":
    main()


