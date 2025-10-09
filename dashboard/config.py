"""
Configurações específicas para o dashboard de análise de preços.
"""

# Configurações de cores e temas
COLORS = {
    'primary': '#00d4ff',
    'secondary': '#0099cc',
    'success': '#00ff00',
    'warning': '#ffaa00',
    'danger': '#ff0000',
    'info': '#00d4ff',
    'light': '#ffffff',
    'dark': '#000000'
}

# Cores para indicadores de discrepância
DISCREPANCY_COLORS = {
    'EXTREME': '#ff0000',
    'HIGH': '#ff6b00',
    'MODERATE': '#ffaa00',
    'LOW': '#00ff00'
}

# Emojis para níveis de discrepância
DISCREPANCY_EMOJIS = {
    'EXTREME': '🔥🔥🔥',
    'HIGH': '🔥🔥',
    'MODERATE': '🔥',
    'LOW': '✅'
}

# Fatores sazonais por cidade
SEASONAL_FACTORS = {
    'Rio de Janeiro': {
        'factors': [1.5, 1.6, 1.2, 1.0, 0.9, 0.85, 0.9, 0.95, 1.0, 1.1, 1.2, 1.7],
        'high_season_months': ['Dec', 'Jan', 'Feb'],
        'description': 'Alta temporada no verão + eventos (Carnaval, Reveillon)'
    },
    'São Paulo': {
        'factors': [1.3, 1.2, 1.0, 0.95, 0.9, 0.9, 1.2, 0.95, 1.0, 1.1, 1.1, 1.4],
        'high_season_months': ['Jan', 'Jul', 'Dec'],
        'description': 'Menos sazonal, picos em férias'
    }
}

# Configurações de layout
LAYOUT_CONFIG = {
    'page_title': 'Rental Price Prediction Dashboard',
    'page_icon': '🏠',
    'layout': 'wide',
    'initial_sidebar_state': 'expanded',
    'chart_height': 700,
    'table_height': 400
}

# Configurações de cache
CACHE_CONFIG = {
    'ttl': 3600,  # 1 hora
    'max_entries': 100
}

# Configurações de dados
DATA_CONFIG = {
    'sample_size': 100,
    'random_seed': 42,
    'price_range': (50, 500),
    'rating_range': (3.0, 5.0)
}

# Configurações de gráficos
CHART_CONFIG = {
    'background_color': 'rgb(20, 23, 30)',
    'paper_bgcolor': 'rgb(14, 17, 23)',
    'font_color': 'white',
    'grid_color': 'rgba(255,255,255,0.1)',
    'hover_mode': 'x unified'
}

# Configurações de métricas
METRICS_CONFIG = {
    'discrepancy_thresholds': {
        'extreme': 50,
        'high': 30,
        'moderate': 15
    },
    'savings_calculation': {
        'high_season_weight': 0.4,
        'regular_season_weight': 0.6
    }
}

# Configurações de recomendações
RECOMMENDATIONS_CONFIG = {
    'best_value_months': 3,
    'avoid_peak_months': 2,
    'revenue_optimization': True
}

# Configurações de filtros
FILTER_CONFIG = {
    'default_cities': ['São Paulo', 'Rio de Janeiro'],
    'default_property_types': ['Entire home', 'Private room', 'Shared room'],
    'price_slider_steps': 10
}

# Configurações de performance
PERFORMANCE_CONFIG = {
    'max_properties_display': 1000,
    'chart_animation': True,
    'lazy_loading': True
}

# Configurações de exportação
EXPORT_CONFIG = {
    'supported_formats': ['csv', 'json', 'excel'],
    'max_export_rows': 10000,
    'include_metadata': True
}

# Configurações de notificações
NOTIFICATIONS_CONFIG = {
    'show_success': True,
    'show_warnings': True,
    'show_errors': True,
    'auto_dismiss': True
}

# Configurações de segurança
SECURITY_CONFIG = {
    'enable_csrf': True,
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'allowed_extensions': ['.csv', '.json', '.xlsx']
}

# Configurações de logging
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'dashboard.log',
    'max_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}
