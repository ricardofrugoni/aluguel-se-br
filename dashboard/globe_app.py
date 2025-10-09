import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from plotly.subplots import make_subplots

# Configuração da página
st.set_page_config(
    page_title="Rental Price Prediction Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #00d4ff, #0099cc);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #00d4ff;
    }
</style>
""", unsafe_allow_html=True)

# Título principal
st.markdown("""
<div class="main-header">
    <h1>🏠 Rental Price Prediction Dashboard</h1>
    <p>Advanced Analytics for Short-Term Rental Pricing in Southeast Brazil</p>
</div>
""", unsafe_allow_html=True)

# Dados simulados para demonstração
@st.cache_data
def load_sample_data():
    """Carrega dados de exemplo para demonstração."""
    np.random.seed(42)
    
    cities = ['São Paulo', 'Rio de Janeiro']
    property_types = ['Entire home', 'Private room', 'Shared room']
    
    data = []
    for city in cities:
        for prop_type in property_types:
            for i in range(50):
                data.append({
                    'id': f"{city}_{prop_type}_{i}",
                    'city': city,
                    'property_type': prop_type,
                    'price': np.random.normal(150, 50) if prop_type == 'Entire home' else np.random.normal(80, 30),
                    'latitude': np.random.uniform(-23.8, -23.3) if city == 'São Paulo' else np.random.uniform(-23.1, -22.8),
                    'longitude': np.random.uniform(-46.8, -46.3) if city == 'São Paulo' else np.random.uniform(-43.4, -43.1),
                    'bedrooms': np.random.randint(1, 4),
                    'bathrooms': np.random.randint(1, 3),
                    'review_scores_rating': np.random.uniform(4.0, 5.0) * 20,
                    'number_of_reviews': np.random.randint(0, 200),
                    'host_is_superhost': np.random.choice(['t', 'f'], p=[0.3, 0.7]),
                    'amenities': '["Wifi", "Kitchen", "Air conditioning", "TV"]'
                })
    
    return pd.DataFrame(data)

# Carregar dados
df = load_sample_data()
df_display = df.copy()

# Sidebar
st.sidebar.title("🎛️ Dashboard Controls")

# Filtros
city_filter = st.sidebar.multiselect(
    "Select Cities:",
    options=df['city'].unique(),
    default=df['city'].unique()
)

property_filter = st.sidebar.multiselect(
    "Select Property Types:",
    options=df['property_type'].unique(),
    default=df['property_type'].unique()
)

price_range = st.sidebar.slider(
    "Price Range (R$/night):",
    min_value=int(df['price'].min()),
    max_value=int(df['price'].max()),
    value=(int(df['price'].min()), int(df['price'].max()))
)

# Aplicar filtros
df_display = df_display[
    (df_display['city'].isin(city_filter)) &
    (df_display['property_type'].isin(property_filter)) &
    (df_display['price'] >= price_range[0]) &
    (df_display['price'] <= price_range[1])
]

# Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Seasonal Analysis", 
    "📊 Market Overview", 
    "🏠 Property Comparison", 
    "🔮 Price Prediction"
])

@st.cache_data
def generate_seasonal_data(base_price, city, property_type='Entire home'):
    """
    Gera dados sazonais simulados com análise percentual e flags de discrepância.
    
    Returns:
        dict com dados sazonais, percentuais e métricas de discrepância
    """
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Fatores sazonais (hemisfério sul)
    if city == 'Rio de Janeiro':
        # Rio: alta temporada no verão + eventos (Carnaval, Reveillon)
        seasonal_factors = [1.5, 1.6, 1.2, 1.0, 0.9, 0.85, 0.9, 0.95, 1.0, 1.1, 1.2, 1.7]
        high_season_months = ['Dec', 'Jan', 'Feb']
        regular_season_months = ['Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov']
    else:  # São Paulo
        # SP: menos sazonal, picos em férias
        seasonal_factors = [1.3, 1.2, 1.0, 0.95, 0.9, 0.9, 1.2, 0.95, 1.0, 1.1, 1.1, 1.4]
        high_season_months = ['Jan', 'Jul', 'Dec']
        regular_season_months = ['Feb', 'Mar', 'Apr', 'May', 'Jun', 'Aug', 'Sep', 'Oct', 'Nov']
    
    # Calcular preços absolutos
    prices = [base_price * factor for factor in seasonal_factors]
    
    # Adicionar variação aleatória realista
    prices = [p * np.random.uniform(0.95, 1.05) for p in prices]
    
    # Calcular variações percentuais em relação ao preço base
    price_variations_pct = [((p - base_price) / base_price * 100) for p in prices]
    
    # Identificar temporadas
    season_type = []
    for month in months:
        if month in high_season_months:
            season_type.append('High Season')
        else:
            season_type.append('Regular Season')
    
    # Calcular métricas de discrepância
    high_season_prices = [prices[i] for i, m in enumerate(months) if m in high_season_months]
    regular_season_prices = [prices[i] for i, m in enumerate(months) if m in regular_season_months]
    
    avg_high_season = np.mean(high_season_prices)
    avg_regular_season = np.mean(regular_season_prices)
    
    # Discrepância percentual (quanto mais caro fica na alta temporada)
    discrepancy_pct = ((avg_high_season - avg_regular_season) / avg_regular_season * 100)
    
    # Classificação de discrepância
    if discrepancy_pct >= 50:
        discrepancy_level = 'EXTREME'
        discrepancy_emoji = '🔥🔥🔥'
        discrepancy_color = '#ff0000'
    elif discrepancy_pct >= 30:
        discrepancy_level = 'HIGH'
        discrepancy_emoji = '🔥🔥'
        discrepancy_color = '#ff6b00'
    elif discrepancy_pct >= 15:
        discrepancy_level = 'MODERATE'
        discrepancy_emoji = '🔥'
        discrepancy_color = '#ffaa00'
    else:
        discrepancy_level = 'LOW'
        discrepancy_emoji = '✅'
        discrepancy_color = '#00ff00'
    
    # Calcular savings (economia se evitar alta temporada)
    potential_savings = avg_high_season - avg_regular_season
    potential_savings_pct = discrepancy_pct
    
    # Mês mais caro e mais barato
    max_price_idx = np.argmax(prices)
    min_price_idx = np.argmin(prices)
    
    max_month = months[max_price_idx]
    min_month = months[min_price_idx]
    
    max_to_min_diff_pct = ((prices[max_price_idx] - prices[min_price_idx]) / prices[min_price_idx] * 100)
    
    return {
        'months': months,
        'prices': prices,
        'seasonal_factors': seasonal_factors,
        'price_variations_pct': price_variations_pct,
        'season_type': season_type,
        'high_season_months': high_season_months,
        'regular_season_months': regular_season_months,
        'metrics': {
            'avg_high_season': avg_high_season,
            'avg_regular_season': avg_regular_season,
            'discrepancy_pct': discrepancy_pct,
            'discrepancy_level': discrepancy_level,
            'discrepancy_emoji': discrepancy_emoji,
            'discrepancy_color': discrepancy_color,
            'potential_savings': potential_savings,
            'potential_savings_pct': potential_savings_pct,
            'max_month': max_month,
            'min_month': min_month,
            'max_price': prices[max_price_idx],
            'min_price': prices[min_price_idx],
            'max_to_min_diff_pct': max_to_min_diff_pct
        }
    }

def create_seasonal_chart(seasonal_data, city, base_price):
    """
    Cria gráfico dual: preços absolutos E variações percentuais.
    """
    
    # Criar subplot com 2 eixos Y
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Price by Month (R$)', 'Variation from Base Price (%)'),
        vertical_spacing=0.15,
        row_heights=[0.6, 0.4]
    )
    
    # ==================== GRÁFICO 1: Preços Absolutos ====================
    
    # Linha de preços
    fig.add_trace(
        go.Scatter(
            x=seasonal_data['months'],
            y=seasonal_data['prices'],
            mode='lines+markers',
            name='Price',
            line=dict(color='#00d4ff', width=3),
            marker=dict(size=10, symbol='circle'),
            fill='tozeroy',
            fillcolor='rgba(0, 212, 255, 0.2)',
            hovertemplate='<b>%{x}</b><br>Price: R$%{y:.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Linha de preço base
    fig.add_trace(
        go.Scatter(
            x=seasonal_data['months'],
            y=[base_price] * 12,
            mode='lines',
            name='Base Price',
            line=dict(color='#ff6b6b', width=2, dash='dash'),
            hovertemplate='Base Price: R$%{y:.2f}<extra></extra>'
        ),
        row=1, col=1
    )
    
    # Destacar alta temporada no fundo
    for month in seasonal_data['high_season_months']:
        if month in seasonal_data['months']:
            idx = seasonal_data['months'].index(month)
            fig.add_vrect(
                x0=idx - 0.4, x1=idx + 0.4,
                fillcolor='rgba(255, 107, 107, 0.15)',
                layer='below',
                line_width=0,
                row=1, col=1
            )
    
    # ==================== GRÁFICO 2: Variações Percentuais ====================
    
    # Cores por tipo de variação
    colors = ['#ff4444' if v > 0 else '#44ff44' for v in seasonal_data['price_variations_pct']]
    
    fig.add_trace(
        go.Bar(
            x=seasonal_data['months'],
            y=seasonal_data['price_variations_pct'],
            name='% Variation',
            marker=dict(
                color=colors,
                line=dict(color='white', width=1)
            ),
            hovertemplate='<b>%{x}</b><br>Variation: %{y:.1f}%<extra></extra>'
        ),
        row=2, col=1
    )
    
    # Linha zero para referência
    fig.add_hline(
        y=0, 
        line_dash="dash", 
        line_color="white", 
        line_width=1,
        row=2, col=1
    )
    
    # ==================== Layout ====================
    
    fig.update_xaxes(title_text="Month", row=2, col=1, gridcolor='rgba(255,255,255,0.1)', color='white')
    fig.update_yaxes(title_text="Price (R$/night)", row=1, col=1, gridcolor='rgba(255,255,255,0.1)', color='white')
    fig.update_yaxes(title_text="Variation (%)", row=2, col=1, gridcolor='rgba(255,255,255,0.1)', color='white')
    
    fig.update_layout(
        title=dict(
            text=f'Seasonal Price Analysis - {city}',
            font=dict(size=18, color='#00d4ff')
        ),
        plot_bgcolor='rgb(20, 23, 30)',
        paper_bgcolor='rgb(14, 17, 23)',
        font=dict(color='white'),
        hovermode='x unified',
        height=700,
        showlegend=True,
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(0,0,0,0.5)'
        )
    )
    
    return fig

def create_discrepancy_indicator(metrics):
    """
    Cria indicador visual de discrepância sazonal.
    """
    html = f"""
    <div style='
        background: linear-gradient(135deg, {metrics['discrepancy_color']}22, {metrics['discrepancy_color']}44);
        border: 2px solid {metrics['discrepancy_color']};
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin: 10px 0;
    '>
        <h2 style='margin: 0; color: {metrics['discrepancy_color']};'>
            {metrics['discrepancy_emoji']} {metrics['discrepancy_level']} SEASONALITY
        </h2>
        <h1 style='margin: 10px 0; color: white; font-size: 3em;'>
            +{metrics['discrepancy_pct']:.1f}%
        </h1>
        <p style='margin: 5px 0; color: #ccc; font-size: 1.2em;'>
            Price increase during high season
        </p>
    </div>
    """
    return html

def create_savings_card(metrics):
    """
    Cria card de economia potencial.
    """
    html = f"""
    <div style='
        background: linear-gradient(135deg, #00ff0022, #00ff0044);
        border: 2px solid #00ff00;
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        margin: 10px 0;
    '>
        <h3 style='margin: 0; color: #00ff00;'>
            💰 POTENTIAL SAVINGS
        </h3>
        <h2 style='margin: 10px 0; color: white; font-size: 2em;'>
            R$ {metrics['potential_savings']:.2f}/night
        </h2>
        <p style='margin: 5px 0; color: #ccc;'>
            Save <b>{metrics['potential_savings_pct']:.1f}%</b> by avoiding high season
        </p>
        <p style='margin: 10px 0; color: #aaa; font-size: 0.9em;'>
            Book in: <b>{', '.join([m for m, s in zip(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], 
            [1.5, 1.6, 1.2, 1.0, 0.9, 0.85, 0.9, 0.95, 1.0, 1.1, 1.2, 1.7]) if s < 1.0][:3])}</b>
        </p>
    </div>
    """
    return html

# ==================== SUBSTITUIR COMPLETAMENTE A TAB1 ====================

with tab1:
    # Seletor manual ou aleatório
    col_a, col_b = st.columns([3, 1])
    
    with col_a:
        selected_idx = st.selectbox(
            "Select a property to analyze:",
            options=df_display.index,
            format_func=lambda x: f"{df_display.loc[x, 'city']} - R${df_display.loc[x, 'price']:.0f} - {df_display.loc[x, 'property_type']}"
        )
    
    with col_b:
        if st.button("🎲 Random Property"):
            selected_idx = df_display.sample(1).index[0]
            st.rerun()
    
    # Dados do imóvel selecionado
    selected_property = df_display.loc[selected_idx]
    
    # Gerar dados sazonais com análise completa
    seasonal_data = generate_seasonal_data(
        selected_property['price'],
        selected_property['city'],
        selected_property['property_type']
    )
    
    metrics = seasonal_data['metrics']
    
    # ==================== SEÇÃO 1: Informações Básicas ====================
    st.markdown("### 🏠 Property Details")
    
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    metric_col1.metric("Base Price", f"R$ {selected_property['price']:.0f}/night")
    metric_col2.metric("City", selected_property['city'])
    metric_col3.metric("Rating", f"{selected_property['review_scores_rating']:.1f}/100")
    metric_col4.metric("Reviews", f"{selected_property['number_of_reviews']:.0f}")
    
    st.markdown("---")
    
    # ==================== SEÇÃO 2: Indicadores de Discrepância ====================
    st.markdown("### 🎯 Seasonality Analysis")
    
    col_ind1, col_ind2 = st.columns(2)
    
    with col_ind1:
        # Indicador de discrepância
        st.markdown(create_discrepancy_indicator(metrics), unsafe_allow_html=True)
        
        # Métricas adicionais
        st.markdown("#### 📊 High vs Regular Season")
        sub_col1, sub_col2 = st.columns(2)
        
        sub_col1.metric(
            "High Season Avg",
            f"R$ {metrics['avg_high_season']:.2f}",
            f"+{((metrics['avg_high_season'] - selected_property['price']) / selected_property['price'] * 100):.1f}%"
        )
        
        sub_col2.metric(
            "Regular Season Avg",
            f"R$ {metrics['avg_regular_season']:.2f}",
            f"{((metrics['avg_regular_season'] - selected_property['price']) / selected_property['price'] * 100):.1f}%"
        )
    
    with col_ind2:
        # Card de economia
        st.markdown(create_savings_card(metrics), unsafe_allow_html=True)
        
        # Extremos
        st.markdown("#### 📈 Price Extremes")
        
        extreme_col1, extreme_col2 = st.columns(2)
        
        extreme_col1.metric(
            f"Peak ({metrics['max_month']})",
            f"R$ {metrics['max_price']:.2f}",
            f"+{((metrics['max_price'] - selected_property['price']) / selected_property['price'] * 100):.1f}%",
            delta_color="inverse"
        )
        
        extreme_col2.metric(
            f"Lowest ({metrics['min_month']})",
            f"R$ {metrics['min_price']:.2f}",
            f"{((metrics['min_price'] - selected_property['price']) / selected_property['price'] * 100):.1f}%",
            delta_color="normal"
        )
        
        st.info(f"💡 **{metrics['max_to_min_diff_pct']:.1f}% cheaper** in {metrics['min_month']} vs {metrics['max_month']}")
    
    st.markdown("---")
    
    # ==================== SEÇÃO 3: Gráficos Detalhados ====================
    st.markdown("### 📊 Detailed Price Analysis")
    
    # Gráfico dual
    seasonal_fig = create_seasonal_chart(
        seasonal_data,
        selected_property['city'],
        selected_property['price']
    )
    st.plotly_chart(seasonal_fig, use_container_width=True)
    
    # ==================== SEÇÃO 4: Tabela Detalhada ====================
    st.markdown("### 📋 Monthly Breakdown")
    
    # Criar DataFrame para tabela
    breakdown_df = pd.DataFrame({
        'Month': seasonal_data['months'],
        'Price (R$)': [f"R$ {p:.2f}" for p in seasonal_data['prices']],
        'Variation (%)': [f"{v:+.1f}%" for v in seasonal_data['price_variations_pct']],
        'Season': seasonal_data['season_type'],
        'Factor': [f"{f:.2f}x" for f in seasonal_data['seasonal_factors']]
    })
    
    # Estilizar tabela
    def highlight_season(row):
        if row['Season'] == 'High Season':
            return ['background-color: rgba(255, 107, 107, 0.2)'] * len(row)
        else:
            return ['background-color: rgba(100, 100, 100, 0.1)'] * len(row)
    
    styled_df = breakdown_df.style.apply(highlight_season, axis=1)
    
    st.dataframe(styled_df, use_container_width=True, height=400)
    
    # ==================== SEÇÃO 5: Recomendações ====================
    st.markdown("### 💡 Smart Booking Recommendations")
    
    rec_col1, rec_col2, rec_col3 = st.columns(3)
    
    with rec_col1:
        st.markdown(f"""
        **🎯 Best Value Months**
        
        Book in **{metrics['min_month']}** for the lowest price:
        - **R$ {metrics['min_price']:.2f}/night**
        - **{((selected_property['price'] - metrics['min_price']) / selected_property['price'] * 100):.1f}% savings**
        - Perfect for budget travelers
        """)
    
    with rec_col2:
        st.markdown(f"""
        **⚠️ Avoid Peak Months**
        
        Skip **{metrics['max_month']}** to save:
        - **R$ {metrics['max_price']:.2f}/night** (peak price)
        - **{metrics['max_to_min_diff_pct']:.1f}% more expensive**
        - Consider shoulder season instead
        """)
    
    with rec_col3:
        st.markdown(f"""
        **📈 Revenue Optimization**
        
        For hosts: maximize revenue in:
        - **High season**: {', '.join(seasonal_data['high_season_months'])}
        - **Premium pricing**: +{metrics['discrepancy_pct']:.1f}% above base
        - **Annual revenue boost**: ~{metrics['discrepancy_pct']*0.3:.1f}%
        """)

# ==================== OUTRAS TABS (PLACEHOLDER) ====================

with tab2:
    st.markdown("### 📊 Market Overview")
    st.info("Market analysis features will be implemented here.")
    
    # Métricas básicas do mercado
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Total Properties", len(df_display))
    col2.metric("Avg Price", f"R$ {df_display['price'].mean():.2f}")
    col3.metric("Avg Rating", f"{df_display['review_scores_rating'].mean():.1f}")
    col4.metric("Superhosts", f"{len(df_display[df_display['host_is_superhost'] == 't'])}")

with tab3:
    st.markdown("### 🏠 Property Comparison")
    st.info("Property comparison features will be implemented here.")
    
    # Comparação básica
    st.dataframe(df_display[['city', 'property_type', 'price', 'review_scores_rating']].head(10))

with tab4:
    st.markdown("### 🔮 Price Prediction")
    st.info("Price prediction features will be implemented here.")
    
    # Formulário de predição
    with st.form("prediction_form"):
        st.markdown("#### Enter Property Details")
        
        pred_city = st.selectbox("City", df['city'].unique())
        pred_type = st.selectbox("Property Type", df['property_type'].unique())
        pred_bedrooms = st.number_input("Bedrooms", min_value=1, max_value=5, value=2)
        pred_bathrooms = st.number_input("Bathrooms", min_value=1, max_value=3, value=1)
        pred_rating = st.slider("Rating", 0.0, 5.0, 4.5)
        
        submitted = st.form_submit_button("Predict Price")
        
        if submitted:
            # Predição simples baseada na média
            base_price = df_display[
                (df_display['city'] == pred_city) & 
                (df_display['property_type'] == pred_type)
            ]['price'].mean()
            
            st.success(f"**Predicted Price: R$ {base_price:.2f}/night**")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>🏠 Rental Price Prediction Dashboard | Powered by Streamlit</p>
    <p>Advanced Analytics for Short-Term Rental Pricing in Southeast Brazil</p>
</div>
""", unsafe_allow_html=True)
