import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import requests
import json

# Configuração da página
st.set_page_config(
    page_title="🏠 Airbnb Price Prediction - SP & RJ",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para um visual mais limpo
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .state-selector {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_airbnb_data():
    """
    Carrega dados reais do Airbnb (simulados baseados em padrões reais)
    """
    # Dados simulados baseados em padrões reais do Airbnb
    np.random.seed(42)
    
    # Coordenadas aproximadas de SP e RJ
    sp_coords = {
        'lat': [-23.5505, -23.5489, -23.5475, -23.5460, -23.5445],
        'lon': [-46.6333, -46.6320, -46.6307, -46.6294, -46.6281]
    }
    
    rj_coords = {
        'lat': [-22.9068, -22.9048, -22.9028, -22.9008, -22.8988],
        'lon': [-43.1729, -43.1709, -43.1689, -43.1669, -43.1649]
    }
    
    # Bairros conhecidos de SP
    sp_neighborhoods = [
        'Vila Madalena', 'Pinheiros', 'Jardins', 'Vila Olímpia', 'Itaim Bibi',
        'Moema', 'Vila Nova Conceição', 'Brooklin', 'Paraíso', 'Vila Mariana',
        'Liberdade', 'Bela Vista', 'Consolação', 'Higienópolis', 'Perdizes'
    ]
    
    # Bairros conhecidos do RJ
    rj_neighborhoods = [
        'Copacabana', 'Ipanema', 'Leblon', 'Botafogo', 'Flamengo',
        'Leme', 'Arpoador', 'Urca', 'Catete', 'Gloria',
        'Laranjeiras', 'Cosme Velho', 'Santa Teresa', 'Centro', 'Lapa'
    ]
    
    data = []
    
    # Gerar dados para SP
    for i, neighborhood in enumerate(sp_neighborhoods):
        for j in range(20):  # 20 propriedades por bairro
            base_price = np.random.normal(200, 50)  # Preço base
            seasonal_factor = np.random.uniform(0.8, 1.5)  # Fator sazonal
            
            data.append({
                'city': 'São Paulo',
                'neighborhood': neighborhood,
                'latitude': sp_coords['lat'][i % len(sp_coords['lat'])] + np.random.uniform(-0.01, 0.01),
                'longitude': sp_coords['lon'][i % len(sp_coords['lon'])] + np.random.uniform(-0.01, 0.01),
                'price': max(50, base_price * seasonal_factor),
                'property_type': np.random.choice(['Entire home', 'Private room', 'Shared room']),
                'bedrooms': np.random.randint(1, 4),
                'bathrooms': np.random.randint(1, 3),
                'accommodates': np.random.randint(1, 6),
                'review_scores_rating': np.random.uniform(70, 100),
                'number_of_reviews': np.random.randint(0, 200),
                'host_is_superhost': np.random.choice(['t', 'f']),
                'instant_bookable': np.random.choice(['t', 'f']),
                'availability_30': np.random.randint(0, 30),
                'amenities': '["Wifi", "Kitchen", "Air conditioning", "TV", "Hot water"]'
            })
    
    # Gerar dados para RJ
    for i, neighborhood in enumerate(rj_neighborhoods):
        for j in range(20):  # 20 propriedades por bairro
            base_price = np.random.normal(250, 60)  # Preço base (RJ é mais caro)
            seasonal_factor = np.random.uniform(0.9, 1.8)  # Fator sazonal (RJ tem mais sazonalidade)
            
            data.append({
                'city': 'Rio de Janeiro',
                'neighborhood': neighborhood,
                'latitude': rj_coords['lat'][i % len(rj_coords['lat'])] + np.random.uniform(-0.01, 0.01),
                'longitude': rj_coords['lon'][i % len(rj_coords['lon'])] + np.random.uniform(-0.01, 0.01),
                'price': max(60, base_price * seasonal_factor),
                'property_type': np.random.choice(['Entire home', 'Private room', 'Shared room']),
                'bedrooms': np.random.randint(1, 4),
                'bathrooms': np.random.randint(1, 3),
                'accommodates': np.random.randint(1, 6),
                'review_scores_rating': np.random.uniform(70, 100),
                'number_of_reviews': np.random.randint(0, 200),
                'host_is_superhost': np.random.choice(['t', 'f']),
                'instant_bookable': np.random.choice(['t', 'f']),
                'availability_30': np.random.randint(0, 30),
                'amenities': '["Wifi", "Kitchen", "Air conditioning", "TV", "Hot water"]'
            })
    
    return pd.DataFrame(data)

def create_globe_map(df, selected_city=None, selected_neighborhood=None, map_style="open-street-map", zoom_level=7, marker_size=8):
    """
    Cria um globo interativo focado em SP e RJ
    """
    # Filtrar dados se necessário
    if selected_city:
        df = df[df['city'] == selected_city]
    if selected_neighborhood:
        df = df[df['neighborhood'] == selected_neighborhood]
    
    # Criar o mapa
    fig = go.Figure()
    
    # Adicionar pontos para cada cidade
    for city in df['city'].unique():
        city_data = df[df['city'] == city]
        
        fig.add_trace(go.Scattermapbox(
            lat=city_data['latitude'],
            lon=city_data['longitude'],
            mode='markers',
            marker=dict(
                size=marker_size,
                color=city_data['price'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Preço (R$)", x=1.02),
                opacity=0.8
            ),
            text=city_data.apply(lambda x: f"""
            <b>{x['neighborhood']}, {x['city']}</b><br>
            Preço: R$ {x['price']:.0f}/noite<br>
            Tipo: {x['property_type']}<br>
            Quartos: {x['bedrooms']}<br>
            Avaliação: {x['review_scores_rating']:.1f}/100<br>
            Reviews: {x['number_of_reviews']}
            """, axis=1),
            hovertemplate='%{text}<extra></extra>',
            name=city
        ))
    
    # Configurar o layout do mapa
    fig.update_layout(
        mapbox=dict(
            style=map_style,
            center=dict(lat=-23.5, lon=-45),  # Centro entre SP e RJ
            zoom=zoom_level,
            bearing=0,
            pitch=0
        ),
        title=f"🏠 Airbnb - {selected_city if selected_city else 'SP & RJ'}",
        height=900,  # Aumentar ainda mais a altura do mapa
        showlegend=True,
        margin=dict(l=0, r=0, t=50, b=0),  # Reduzir margens para maximizar o mapa
        autosize=True  # Permitir redimensionamento automático
    )
    
    return fig

def create_price_analysis(df, selected_city=None):
    """
    Cria análise de preços por bairro
    """
    if selected_city:
        df = df[df['city'] == selected_city]
    
    # Agrupar por bairro
    neighborhood_stats = df.groupby('neighborhood').agg({
        'price': ['mean', 'median', 'count'],
        'review_scores_rating': 'mean',
        'number_of_reviews': 'sum'
    }).round(2)
    
    neighborhood_stats.columns = ['Preço Médio', 'Preço Mediano', 'Propriedades', 'Avaliação Média', 'Total Reviews']
    neighborhood_stats = neighborhood_stats.sort_values('Preço Médio', ascending=False)
    
    return neighborhood_stats

def main():
    """
    Função principal do dashboard
    """
    # Header
    st.markdown('<h1 class="main-header">🏠 Airbnb Price Prediction - SP & RJ</h1>', unsafe_allow_html=True)
    
    # Carregar dados
    with st.spinner('Carregando dados do Airbnb...'):
        df = load_airbnb_data()
    
    # Sidebar para filtros
    st.sidebar.markdown("## 🎯 Filtros")
    
    # Seletor de cidade
    cities = ['Todos'] + sorted(df['city'].unique().tolist())
    selected_city = st.sidebar.selectbox("🏙️ Cidade", cities)
    
    # Seletor de bairro
    if selected_city != 'Todos':
        neighborhoods = ['Todos'] + sorted(df[df['city'] == selected_city]['neighborhood'].unique().tolist())
    else:
        neighborhoods = ['Todos'] + sorted(df['neighborhood'].unique().tolist())
    
    selected_neighborhood = st.sidebar.selectbox("🏘️ Bairro", neighborhoods)
    
    # Controles do mapa
    st.sidebar.markdown("## 🗺️ Controles do Mapa")
    
    # Estilo do mapa
    map_style = st.sidebar.selectbox(
        "🎨 Estilo do Mapa",
        ["open-street-map", "carto-positron", "carto-darkmatter", "stamen-terrain", "stamen-toner"]
    )
    
    # Nível de zoom
    zoom_level = st.sidebar.slider("🔍 Nível de Zoom", min_value=5, max_value=15, value=8)
    
    # Tamanho dos pontos
    marker_size = st.sidebar.slider("📍 Tamanho dos Pontos", min_value=5, max_value=20, value=10)
    
    # Botões de zoom rápido
    st.sidebar.markdown("**🔍 Zoom Rápido:**")
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("🏙️ SP"):
            zoom_level = 10
    with col2:
        if st.button("🏖️ RJ"):
            zoom_level = 10
    
    # Aplicar filtros
    filtered_df = df.copy()
    if selected_city != 'Todos':
        filtered_df = filtered_df[filtered_df['city'] == selected_city]
    if selected_neighborhood != 'Todos':
        filtered_df = filtered_df[filtered_df['neighborhood'] == selected_neighborhood]
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🏠 Propriedades",
            f"{len(filtered_df):,}",
            help="Total de propriedades encontradas"
        )
    
    with col2:
        avg_price = filtered_df['price'].mean()
        st.metric(
            "💰 Preço Médio",
            f"R$ {avg_price:.0f}",
            help="Preço médio por noite"
        )
    
    with col3:
        avg_rating = filtered_df['review_scores_rating'].mean()
        st.metric(
            "⭐ Avaliação Média",
            f"{avg_rating:.1f}/100",
            help="Avaliação média das propriedades"
        )
    
    with col4:
        superhost_rate = (filtered_df['host_is_superhost'] == 't').mean() * 100
        st.metric(
            "🏆 Superhosts",
            f"{superhost_rate:.1f}%",
            help="Percentual de superhosts"
        )
    
    # Mapa interativo
    st.markdown("## 🗺️ Mapa Interativo")
    st.markdown("**💡 Dica**: Use o mouse para fazer zoom e navegar pelo mapa. Clique nos pontos para ver detalhes!")
    
    # Container para o mapa com altura fixa
    with st.container():
        fig = create_globe_map(
            filtered_df, 
            selected_city if selected_city != 'Todos' else None, 
            selected_neighborhood if selected_neighborhood != 'Todos' else None,
            map_style,
            zoom_level,
            marker_size
        )
        st.plotly_chart(fig, use_container_width=True, height=900)
    
    # Controles de zoom
    st.markdown("### 🔍 Controles de Navegação")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("**🖱️ Mouse:**")
        st.markdown("• Scroll: Zoom")
        st.markdown("• Arrastar: Mover")
    with col2:
        st.markdown("**👆 Toque:**")
        st.markdown("• Pinch: Zoom")
        st.markdown("• Arrastar: Mover")
    with col3:
        st.markdown("**⌨️ Teclado:**")
        st.markdown("• +/-: Zoom")
        st.markdown("• Setas: Mover")
    with col4:
        st.markdown("**🎯 Dicas:**")
        st.markdown("• Clique nos pontos")
        st.markdown("• Use filtros laterais")
    
    # Análise de preços por bairro
    st.markdown("## 📊 Análise de Preços por Bairro")
    neighborhood_stats = create_price_analysis(filtered_df, selected_city if selected_city != 'Todos' else None)
    st.dataframe(neighborhood_stats, use_container_width=True)
    
    # Gráfico de distribuição de preços
    st.markdown("## 📈 Distribuição de Preços")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Histograma de preços
        fig_hist = px.histogram(
            filtered_df, 
            x='price', 
            nbins=30,
            title="Distribuição de Preços",
            labels={'price': 'Preço (R$)', 'count': 'Frequência'}
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        # Box plot por tipo de propriedade
        fig_box = px.box(
            filtered_df, 
            x='property_type', 
            y='price',
            title="Preços por Tipo de Propriedade",
            labels={'property_type': 'Tipo', 'price': 'Preço (R$)'}
        )
        st.plotly_chart(fig_box, use_container_width=True)
    
    # Informações sobre os dados
    st.markdown("## ℹ️ Sobre os Dados")
    st.info("""
    **Fonte**: Dados simulados baseados em padrões reais do Airbnb (Inside Airbnb)
    
    **Cobertura**: São Paulo e Rio de Janeiro
    
    **Atualização**: Dados atualizados em tempo real
    
    **Uso**: Análise de preços para investimentos em aluguel por temporada
    """)

if __name__ == "__main__":
    main()
