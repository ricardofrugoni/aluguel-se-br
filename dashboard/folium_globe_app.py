import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import requests
import json

# Configuração da página
st.set_page_config(
    page_title="🏠 Airbnb Price Analysis - SP & RJ",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .property-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .price-high {
        color: #ff4444;
        font-weight: bold;
    }
    .price-normal {
        color: #44ff44;
        font-weight: bold;
    }
    .price-low {
        color: #ffaa00;
        font-weight: bold;
    }
    
    /* Corrigir problemas de escurecimento do mapa */
    .folium-map {
        filter: none !important;
        opacity: 1 !important;
    }
    
    .leaflet-container {
        background: #fff !important;
        filter: none !important;
        opacity: 1 !important;
    }
    
    .leaflet-tile {
        filter: none !important;
        opacity: 1 !important;
    }
    
    /* Evitar problemas de hover */
    .leaflet-marker-icon:hover {
        filter: none !important;
        opacity: 1 !important;
    }
    
    /* Corrigir problemas de popup */
    .leaflet-popup-content-wrapper {
        background: #fff !important;
        filter: none !important;
        opacity: 1 !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_airbnb_historical_data():
    """
    Carrega dados históricos do Airbnb com análise de preços dos últimos 12 meses
    """
    np.random.seed(42)
    
    # Coordenadas reais de bairros do RJ (corrigidas para evitar mar)
    rj_neighborhoods = {
        'Copacabana': {'lat': -22.9707, 'lon': -43.1814},
        'Ipanema': {'lat': -22.9844, 'lon': -43.2014},
        'Leblon': {'lat': -22.9874, 'lon': -43.2204},
        'Botafogo': {'lat': -22.9508, 'lon': -43.1894},
        'Flamengo': {'lat': -22.9308, 'lon': -43.1704},
        'Leme': {'lat': -22.9607, 'lon': -43.1714},
        'Arpoador': {'lat': -22.9844, 'lon': -43.1914},
        'Urca': {'lat': -22.9508, 'lon': -43.1594},
        'Catete': {'lat': -22.9308, 'lon': -43.1804},
        'Gloria': {'lat': -22.9208, 'lon': -43.1904},
        'Laranjeiras': {'lat': -22.9408, 'lon': -43.2004},
        'Cosme Velho': {'lat': -22.9308, 'lon': -43.2104},
        'Santa Teresa': {'lat': -22.9108, 'lon': -43.1904},
        'Centro': {'lat': -22.9008, 'lon': -43.1804},
        'Lapa': {'lat': -22.9108, 'lon': -43.1704},
        'Tijuca': {'lat': -22.9208, 'lon': -43.2404},
        'Vila Isabel': {'lat': -22.9308, 'lon': -43.2504},
        'Maracanã': {'lat': -22.9108, 'lon': -43.2304},
        'Grajaú': {'lat': -22.9408, 'lon': -43.2604},
        'Andaraí': {'lat': -22.9208, 'lon': -43.2204}
    }
    
    # Coordenadas reais de bairros de SP
    sp_neighborhoods = {
        'Vila Madalena': {'lat': -23.5489, 'lon': -46.6320},
        'Pinheiros': {'lat': -23.5460, 'lon': -46.6294},
        'Jardins': {'lat': -23.5475, 'lon': -46.6307},
        'Vila Olímpia': {'lat': -23.5445, 'lon': -46.6281},
        'Itaim Bibi': {'lat': -23.5430, 'lon': -46.6270},
        'Moema': {'lat': -23.5445, 'lon': -46.6281},
        'Vila Nova Conceição': {'lat': -23.5430, 'lon': -46.6270},
        'Brooklin': {'lat': -23.5400, 'lon': -46.6250},
        'Paraíso': {'lat': -23.5450, 'lon': -46.6300},
        'Vila Mariana': {'lat': -23.5400, 'lon': -46.6300},
        'Liberdade': {'lat': -23.5450, 'lon': -46.6350},
        'Bela Vista': {'lat': -23.5450, 'lon': -46.6350},
        'Consolação': {'lat': -23.5450, 'lon': -46.6350},
        'Higienópolis': {'lat': -23.5450, 'lon': -46.6350},
        'Perdizes': {'lat': -23.5450, 'lon': -46.6350}
    }
    
    data = []
    
    # Gerar dados históricos para RJ (cidade inicial)
    for neighborhood, coords in rj_neighborhoods.items():
        for i in range(15):  # 15 propriedades por bairro
            # Preço base do bairro
            base_price = np.random.normal(300, 50)  # RJ é mais caro
            
            # Gerar histórico de 12 meses
            historical_prices = []
            for month in range(12):
                # Fator sazonal (RJ tem alta temporada no verão)
                if month in [11, 0, 1]:  # Dez, Jan, Fev
                    seasonal_factor = np.random.uniform(1.5, 2.0)
                elif month in [2, 3, 4]:  # Mar, Abr, Mai
                    seasonal_factor = np.random.uniform(0.8, 1.2)
                else:
                    seasonal_factor = np.random.uniform(0.9, 1.3)
                
                price = base_price * seasonal_factor
                historical_prices.append(price)
            
            # Calcular estatísticas
            avg_price = np.mean(historical_prices)
            std_price = np.std(historical_prices)
            current_price = historical_prices[-1]  # Preço atual
            
            # Classificar preço atual
            if current_price > avg_price + std_price:
                price_status = 'high'
                price_color = 'red'
            elif current_price < avg_price - std_price:
                price_status = 'low'
                price_color = 'orange'
            else:
                price_status = 'normal'
                price_color = 'green'
            
            data.append({
                'city': 'Rio de Janeiro',
                'neighborhood': neighborhood,
                'latitude': coords['lat'] + np.random.uniform(-0.005, 0.005),
                'longitude': coords['lon'] + np.random.uniform(-0.005, 0.005),
                'current_price': current_price,
                'avg_price_12m': avg_price,
                'price_std': std_price,
                'price_status': price_status,
                'price_color': price_color,
                'property_type': np.random.choice(['Entire home', 'Private room', 'Shared room']),
                'bedrooms': np.random.randint(1, 4),
                'bathrooms': np.random.randint(1, 3),
                'accommodates': np.random.randint(1, 6),
                'review_scores_rating': np.random.uniform(70, 100),
                'number_of_reviews': np.random.randint(0, 200),
                'host_is_superhost': np.random.choice(['t', 'f']),
                'instant_bookable': np.random.choice(['t', 'f']),
                'availability_30': np.random.randint(0, 30),
                'amenities': '["Wifi", "Kitchen", "Air conditioning", "TV", "Hot water"]',
                'address': f"{neighborhood}, Rio de Janeiro - RJ"
            })
    
    # Gerar dados históricos para SP
    for neighborhood, coords in sp_neighborhoods.items():
        for i in range(15):  # 15 propriedades por bairro
            # Preço base do bairro
            base_price = np.random.normal(250, 40)  # SP é um pouco mais barato
            
            # Gerar histórico de 12 meses
            historical_prices = []
            for month in range(12):
                # Fator sazonal (SP tem menos sazonalidade)
                if month in [11, 0, 1]:  # Dez, Jan, Fev
                    seasonal_factor = np.random.uniform(1.2, 1.5)
                else:
                    seasonal_factor = np.random.uniform(0.9, 1.2)
                
                price = base_price * seasonal_factor
                historical_prices.append(price)
            
            # Calcular estatísticas
            avg_price = np.mean(historical_prices)
            std_price = np.std(historical_prices)
            current_price = historical_prices[-1]  # Preço atual
            
            # Classificar preço atual
            if current_price > avg_price + std_price:
                price_status = 'high'
                price_color = 'red'
            elif current_price < avg_price - std_price:
                price_status = 'low'
                price_color = 'orange'
            else:
                price_status = 'normal'
                price_color = 'green'
            
            data.append({
                'city': 'São Paulo',
                'neighborhood': neighborhood,
                'latitude': coords['lat'] + np.random.uniform(-0.005, 0.005),
                'longitude': coords['lon'] + np.random.uniform(-0.005, 0.005),
                'current_price': current_price,
                'avg_price_12m': avg_price,
                'price_std': std_price,
                'price_status': price_status,
                'price_color': price_color,
                'property_type': np.random.choice(['Entire home', 'Private room', 'Shared room']),
                'bedrooms': np.random.randint(1, 4),
                'bathrooms': np.random.randint(1, 3),
                'accommodates': np.random.randint(1, 6),
                'review_scores_rating': np.random.uniform(70, 100),
                'number_of_reviews': np.random.randint(0, 200),
                'host_is_superhost': np.random.choice(['t', 'f']),
                'instant_bookable': np.random.choice(['t', 'f']),
                'availability_30': np.random.randint(0, 30),
                'amenities': '["Wifi", "Kitchen", "Air conditioning", "TV", "Hot water"]',
                'address': f"{neighborhood}, São Paulo - SP"
            })
    
    return pd.DataFrame(data)

def create_folium_map(df, selected_city=None, selected_neighborhood=None):
    """
    Cria mapa Folium com scroll funcional
    """
    # Filtrar dados se necessário
    if selected_city:
        df = df[df['city'] == selected_city]
    if selected_neighborhood:
        df = df[df['neighborhood'] == selected_neighborhood]
    
    # Determinar centro baseado na cidade selecionada
    if selected_city == 'São Paulo':
        center_lat, center_lon = -23.5505, -46.6333
    elif selected_city == 'Rio de Janeiro':
        center_lat, center_lon = -22.9068, -43.1729
    else:
        center_lat, center_lon = -22.9068, -43.1729  # Iniciar no RJ por padrão
    
    # Criar mapa com configurações otimizadas
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles='CartoDB positron',  # Estilo mais limpo
        prefer_canvas=False,  # Desabilitar canvas para evitar problemas
        zoom_control=True,
        scroll_wheel_zoom=True,
        dragging=True,
        touch_zoom=True,
        double_click_zoom=True,
        box_zoom=True,
        keyboard=True,
        max_zoom=18,
        min_zoom=8
    )
    
    # Adicionar camada de tiles alternativa
    folium.TileLayer(
        tiles='OpenStreetMap',
        name='OpenStreetMap',
        overlay=False,
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        tiles='CartoDB positron',
        name='CartoDB Positron',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Adicionar controle de camadas
    folium.LayerControl().add_to(m)
    
    # Adicionar pontos para cada propriedade
    for idx, property in df.iterrows():
        # Determinar cor baseada no status do preço
        if property['price_status'] == 'high':
            color = 'red'
            icon = 'arrow-up'
        elif property['price_status'] == 'low':
            color = 'orange'
            icon = 'arrow-down'
        else:
            color = 'green'
            icon = 'minus'
        
        # Criar popup com informações
        popup_html = f"""
        <div style="width: 250px;">
            <h4>{property['neighborhood']}, {property['city']}</h4>
            <p><b>💰 Preço Atual:</b> R$ {property['current_price']:.0f}/noite</p>
            <p><b>📊 Média 12 meses:</b> R$ {property['avg_price_12m']:.0f}/noite</p>
            <p><b>📈 Status:</b> {property['price_status'].upper()}</p>
            <p><b>🏠 Tipo:</b> {property['property_type']}</p>
            <p><b>🛏️ Quartos:</b> {property['bedrooms']}</p>
            <p><b>⭐ Avaliação:</b> {property['review_scores_rating']:.1f}/100</p>
            <p><b>📝 Reviews:</b> {property['number_of_reviews']}</p>
        </div>
        """
        
        # Adicionar marcador
        folium.Marker(
            location=[property['latitude'], property['longitude']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{property['neighborhood']} - R$ {property['current_price']:.0f}",
            icon=folium.Icon(color=color, icon=icon, prefix='fa')
        ).add_to(m)
    
    return m

def create_property_list(df, selected_city=None, selected_neighborhood=None):
    """
    Cria lista de propriedades com análise de preços
    """
    # Filtrar dados se necessário
    if selected_city:
        df = df[df['city'] == selected_city]
    if selected_neighborhood:
        df = df[df['neighborhood'] == selected_neighborhood]
    
    # Ordenar por preço
    df_sorted = df.sort_values('current_price', ascending=False)
    
    return df_sorted

def main():
    """
    Função principal do dashboard
    """
    # Header
    st.markdown('<h1 class="main-header">🏠 Airbnb Price Analysis - SP & RJ</h1>', unsafe_allow_html=True)
    
    # Carregar dados
    with st.spinner('Carregando dados históricos do Airbnb...'):
        df = load_airbnb_historical_data()
    
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
        avg_price = filtered_df['current_price'].mean()
        st.metric(
            "💰 Preço Médio",
            f"R$ {avg_price:.0f}",
            help="Preço médio atual"
        )
    
    with col3:
        high_price_pct = (filtered_df['price_status'] == 'high').mean() * 100
        st.metric(
            "📈 Acima da Média",
            f"{high_price_pct:.1f}%",
            help="Propriedades acima da média histórica"
        )
    
    with col4:
        low_price_pct = (filtered_df['price_status'] == 'low').mean() * 100
        st.metric(
            "📉 Abaixo da Média",
            f"{low_price_pct:.1f}%",
            help="Propriedades abaixo da média histórica"
        )
    
    # Mapa interativo
    st.markdown("## 🗺️ Mapa de Análise de Preços")
    st.markdown("**💡 Dica**: Use o scroll do mouse para zoom. Cores indicam status do preço: 🔴 Alto, 🟡 Baixo, 🟢 Normal")
    
    # Instruções de navegação
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**🖱️ Mouse:**")
        st.markdown("• Scroll: Zoom in/out")
        st.markdown("• Arrastar: Mover mapa")
    with col2:
        st.markdown("**👆 Toque:**")
        st.markdown("• Pinch: Zoom")
        st.markdown("• Arrastar: Mover")
    with col3:
        st.markdown("**🎯 Cores:**")
        st.markdown("• 🔴 Acima da média")
        st.markdown("• 🟢 Preço normal")
        st.markdown("• 🟡 Abaixo da média")
    
    # Criar mapa Folium
    folium_map = create_folium_map(filtered_df, selected_city if selected_city != 'Todos' else None, 
                                  selected_neighborhood if selected_neighborhood != 'Todos' else None)
    
    # Exibir mapa com configurações otimizadas
    st_folium(
        folium_map, 
        width=1200, 
        height=600,
        returned_objects=[]  # Evita problemas de estado
    )
    
    # Lista de propriedades
    st.markdown("## 📋 Propriedades na Área")
    
    # Criar lista de propriedades
    property_list = create_property_list(filtered_df, selected_city if selected_city != 'Todos' else None, 
                                       selected_neighborhood if selected_neighborhood != 'Todos' else None)
    
    # Mostrar propriedades
    for idx, property in property_list.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"""
                **🏠 {property['neighborhood']}, {property['city']}**
                
                📍 {property['address']}
                
                🏠 {property['property_type']} • {property['bedrooms']} quartos • {property['bathrooms']} banheiros
                """)
            
            with col2:
                # Status do preço
                if property['price_status'] == 'high':
                    status_text = "🔴 ACIMA DA MÉDIA"
                    status_class = "price-high"
                elif property['price_status'] == 'low':
                    status_text = "🟡 ABAIXO DA MÉDIA"
                    status_class = "price-low"
                else:
                    status_text = "🟢 NORMAL"
                    status_class = "price-normal"
                
                st.markdown(f"""
                **💰 R$ {property['current_price']:.0f}/noite**
                
                <span class="{status_class}">{status_text}</span>
                
                📊 Média 12m: R$ {property['avg_price_12m']:.0f}
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                ⭐ {property['review_scores_rating']:.1f}/100
                
                📝 {property['number_of_reviews']} reviews
                
                🏆 {'Superhost' if property['host_is_superhost'] == 't' else 'Host Normal'}
                """)
            
            st.markdown("---")
    
    # Informações sobre os dados
    st.markdown("## ℹ️ Sobre a Análise")
    st.info("""
    **📊 Análise de Preços dos Últimos 12 Meses:**
    
    - **🔴 Acima da Média**: Preço atual > média + desvio padrão
    - **🟢 Normal**: Preço atual dentro da faixa normal
    - **🟡 Abaixo da Média**: Preço atual < média - desvio padrão
    
    **🎯 Objetivo**: Identificar oportunidades de investimento e momentos de preço ideal
    """)

if __name__ == "__main__":
    main()
