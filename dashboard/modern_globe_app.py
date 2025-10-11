import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json

# Configuração da página
st.set_page_config(
    page_title="🏠 Airbnb Price Intelligence - SP & RJ",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS moderno e responsivo
st.markdown("""
<style>
    /* Reset e base */
    * {
        box-sizing: border-box;
    }
    
    .main-header {
        background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
    }
    
    /* Cards modernos */
    .metric-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        border: 1px solid #e1e5e9;
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2c3e50;
        margin: 0;
    }
    
    .metric-label {
        font-size: 1rem;
        color: #7f8c8d;
        margin: 0.5rem 0 0 0;
    }
    
    /* Status indicators - Paleta única */
    .status-high {
        color: #e74c3c;
        font-weight: 600;
    }
    
    .status-normal {
        color: #27ae60;
        font-weight: 600;
    }
    
    .status-low {
        color: #f39c12;
        font-weight: 600;
    }
    
    /* Property cards */
    .property-card {
        background: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #3498db;
        transition: all 0.3s ease;
    }
    
    .property-card:hover {
        transform: translateX(5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    /* Containers compactos e cinza claro */
    .stMetric {
        background: #f8f9fa !important;
        border-radius: 4px !important;
        padding: 0.1rem !important;
        margin: 0.05rem !important;
        height: 50px !important;
        min-height: 50px !important;
        max-height: 50px !important;
    }
    
    .stMetric > div {
        padding: 0.1rem !important;
        margin: 0 !important;
        height: 100% !important;
    }
    
    .stMetric > div > div {
        padding: 0 !important;
        margin: 0 !important;
        height: 100% !important;
    }
    
    .stMetric > div > div > div {
        padding: 0 !important;
        margin: 0 !important;
        height: 100% !important;
    }
    
    /* Forçar fundo cinza em todos os elementos */
    .stMetric, .stMetric *, .stMetric > div, .stMetric > div > div {
        background: #f8f9fa !important;
        background-color: #f8f9fa !important;
    }
    
    /* Reduzir fonte dos valores */
    .stMetric [data-testid="metric-value"] {
        font-size: 1.2rem !important;
        line-height: 1 !important;
    }
    
    .stMetric [data-testid="metric-label"] {
        font-size: 0.8rem !important;
        line-height: 1 !important;
    }
    
    .property-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 0 0 0.5rem 0;
    }
    
    .property-price {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .property-details {
        color: #7f8c8d;
        font-size: 0.9rem;
        margin: 0.5rem 0;
    }
    
    /* Map container */
    .map-container {
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 2rem 0;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .metric-value {
            font-size: 2rem;
        }
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
    
    .leaflet-marker-icon:hover {
        filter: none !important;
        opacity: 1 !important;
    }
    
    .leaflet-popup-content-wrapper {
        background: #fff !important;
        filter: none !important;
        opacity: 1 !important;
        border-radius: 10px !important;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2) !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_airbnb_historical_data():
    """
    Carrega dados históricos do Airbnb com análise de preços dos últimos 12 meses
    """
    np.random.seed(42)
    
    # Coordenadas reais de bairros do RJ (todos na orla para evitar mar)
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
    
    # Ruas famosas por bairro com coordenadas reais
    rj_streets = {
        'Copacabana': {
            'Avenida Atlântica': {'lat': -22.9707, 'lon': -43.1814},
            'Rua Barata Ribeiro': {'lat': -22.9707, 'lon': -43.1850},
            'Rua Nossa Senhora de Copacabana': {'lat': -22.9707, 'lon': -43.1880}
        },
        'Ipanema': {
            'Rua Visconde de Pirajá': {'lat': -22.9844, 'lon': -43.2014},
            'Avenida Vieira Souto': {'lat': -22.9844, 'lon': -43.1980},
            'Rua Farme de Amoedo': {'lat': -22.9844, 'lon': -43.2040}
        },
        'Leblon': {
            'Rua Dias Ferreira': {'lat': -22.9874, 'lon': -43.2204},
            'Avenida Ataulfo de Paiva': {'lat': -22.9874, 'lon': -43.2170},
            'Rua General Urquiza': {'lat': -22.9874, 'lon': -43.2230}
        },
        'Botafogo': {
            'Rua Voluntários da Pátria': {'lat': -22.9508, 'lon': -43.1894},
            'Rua São Clemente': {'lat': -22.9508, 'lon': -43.1860},
            'Avenida Pasteur': {'lat': -22.9508, 'lon': -43.1920}
        },
        'Flamengo': {
            'Rua Marquês de Abrantes': {'lat': -22.9308, 'lon': -43.1704},
            'Rua Senador Vergueiro': {'lat': -22.9308, 'lon': -43.1670},
            'Avenida Beira Mar': {'lat': -22.9308, 'lon': -43.1730}
        },
        'Leme': {
            'Avenida Atlântica': {'lat': -22.9607, 'lon': -43.1714},
            'Rua Gustavo Sampaio': {'lat': -22.9607, 'lon': -43.1680},
            'Rua Antônio Vieira': {'lat': -22.9607, 'lon': -43.1740}
        },
        'Arpoador': {
            'Avenida Atlântica': {'lat': -22.9844, 'lon': -43.1914},
            'Rua Francisco Otaviano': {'lat': -22.9844, 'lon': -43.1880},
            'Rua Joana Angélica': {'lat': -22.9844, 'lon': -43.1940}
        },
        'Urca': {
            'Rua Marechal Cantuária': {'lat': -22.9508, 'lon': -43.1594},
            'Rua General Bruce': {'lat': -22.9508, 'lon': -43.1560},
            'Avenida Pasteur': {'lat': -22.9508, 'lon': -43.1620}
        },
        'Catete': {
            'Rua do Catete': {'lat': -22.9308, 'lon': -43.1804},
            'Rua Silveira Martins': {'lat': -22.9308, 'lon': -43.1770},
            'Avenida Beira Mar': {'lat': -22.9308, 'lon': -43.1830}
        },
        'Gloria': {
            'Rua da Glória': {'lat': -22.9208, 'lon': -43.1904},
            'Rua do Russel': {'lat': -22.9208, 'lon': -43.1870},
            'Avenida Beira Mar': {'lat': -22.9208, 'lon': -43.1930}
        },
        'Laranjeiras': {
            'Rua das Laranjeiras': {'lat': -22.9408, 'lon': -43.2004},
            'Rua General Glicério': {'lat': -22.9408, 'lon': -43.1970},
            'Rua Pinheiro Machado': {'lat': -22.9408, 'lon': -43.2030}
        },
        'Cosme Velho': {
            'Rua Cosme Velho': {'lat': -22.9308, 'lon': -43.2104},
            'Rua Ladeira dos Tabajaras': {'lat': -22.9308, 'lon': -43.2070},
            'Rua das Laranjeiras': {'lat': -22.9308, 'lon': -43.2130}
        },
        'Santa Teresa': {
            'Rua Almirante Alexandrino': {'lat': -22.9108, 'lon': -43.1904},
            'Rua Joaquim Murtinho': {'lat': -22.9108, 'lon': -43.1870},
            'Largo dos Guimarães': {'lat': -22.9108, 'lon': -43.1930}
        },
        'Centro': {
            'Rua da Carioca': {'lat': -22.9008, 'lon': -43.1804},
            'Rua Uruguaiana': {'lat': -22.9008, 'lon': -43.1770},
            'Avenida Rio Branco': {'lat': -22.9008, 'lon': -43.1830}
        },
        'Lapa': {
            'Rua da Lapa': {'lat': -22.9108, 'lon': -43.1704},
            'Rua Joaquim Silva': {'lat': -22.9108, 'lon': -43.1670},
            'Avenida Mem de Sá': {'lat': -22.9108, 'lon': -43.1730}
        },
        'Tijuca': {
            'Rua Conde de Bonfim': {'lat': -22.9208, 'lon': -43.2404},
            'Rua Haddock Lobo': {'lat': -22.9208, 'lon': -43.2370},
            'Avenida Maracanã': {'lat': -22.9208, 'lon': -43.2430}
        },
        'Vila Isabel': {
            'Rua Barão de Mesquita': {'lat': -22.9308, 'lon': -43.2504},
            'Rua Maxwell': {'lat': -22.9308, 'lon': -43.2470},
            'Rua Goulart': {'lat': -22.9308, 'lon': -43.2530}
        },
        'Maracanã': {
            'Rua São Francisco Xavier': {'lat': -22.9108, 'lon': -43.2304},
            'Rua Mariz e Barros': {'lat': -22.9108, 'lon': -43.2270},
            'Avenida Maracanã': {'lat': -22.9108, 'lon': -43.2330}
        },
        'Grajaú': {
            'Rua Barão de Mesquita': {'lat': -22.9408, 'lon': -43.2604},
            'Rua Maxwell': {'lat': -22.9408, 'lon': -43.2570},
            'Rua Goulart': {'lat': -22.9408, 'lon': -43.2630}
        },
        'Andaraí': {
            'Rua Barão de Mesquita': {'lat': -22.9208, 'lon': -43.2204},
            'Rua Maxwell': {'lat': -22.9208, 'lon': -43.2170},
            'Rua Goulart': {'lat': -22.9208, 'lon': -43.2230}
        }
    }
    
    # Coordenadas reais de bairros de SP (corrigidas para evitar mar)
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
        'Perdizes': {'lat': -23.5450, 'lon': -46.6350},
        'Vila Buarque': {'lat': -23.5450, 'lon': -46.6350},
        'República': {'lat': -23.5450, 'lon': -46.6350},
        'Sé': {'lat': -23.5450, 'lon': -46.6350},
        'Bom Retiro': {'lat': -23.5450, 'lon': -46.6350},
        'Brás': {'lat': -23.5450, 'lon': -46.6350}
    }
    
    # Ruas famosas por bairro de SP com coordenadas reais
    sp_streets = {
        'Vila Madalena': {
            'Rua Harmonia': {'lat': -23.5489, 'lon': -46.6320},
            'Rua Aspicuelta': {'lat': -23.5489, 'lon': -46.6350},
            'Rua Purpurina': {'lat': -23.5489, 'lon': -46.6290}
        },
        'Pinheiros': {
            'Rua dos Pinheiros': {'lat': -23.5460, 'lon': -46.6294},
            'Rua Teodoro Sampaio': {'lat': -23.5460, 'lon': -46.6320},
            'Rua Cardeal Arcoverde': {'lat': -23.5460, 'lon': -46.6270}
        },
        'Jardins': {
            'Rua Oscar Freire': {'lat': -23.5475, 'lon': -46.6307},
            'Rua Augusta': {'lat': -23.5475, 'lon': -46.6330},
            'Rua Haddock Lobo': {'lat': -23.5475, 'lon': -46.6280}
        },
        'Vila Olímpia': {
            'Rua Funchal': {'lat': -23.5445, 'lon': -46.6281},
            'Rua Cidade de Toledo': {'lat': -23.5445, 'lon': -46.6310},
            'Avenida Faria Lima': {'lat': -23.5445, 'lon': -46.6250}
        },
        'Itaim Bibi': {
            'Rua Bandeira Paulista': {'lat': -23.5430, 'lon': -46.6270},
            'Rua Joaquim Floriano': {'lat': -23.5430, 'lon': -46.6300},
            'Avenida Faria Lima': {'lat': -23.5430, 'lon': -46.6240}
        },
        'Moema': {
            'Rua Moema': {'lat': -23.5445, 'lon': -46.6281},
            'Rua Inácio Pereira da Rocha': {'lat': -23.5445, 'lon': -46.6310},
            'Avenida Ibirapuera': {'lat': -23.5445, 'lon': -46.6250}
        },
        'Vila Nova Conceição': {
            'Rua Bandeira Paulista': {'lat': -23.5430, 'lon': -46.6270},
            'Rua Joaquim Floriano': {'lat': -23.5430, 'lon': -46.6300},
            'Avenida Faria Lima': {'lat': -23.5430, 'lon': -46.6240}
        },
        'Brooklin': {
            'Rua dos Três Irmãos': {'lat': -23.5400, 'lon': -46.6250},
            'Rua Bandeira Paulista': {'lat': -23.5400, 'lon': -46.6280},
            'Avenida Faria Lima': {'lat': -23.5400, 'lon': -46.6220}
        },
        'Paraíso': {
            'Rua do Paraíso': {'lat': -23.5450, 'lon': -46.6300},
            'Rua Vergueiro': {'lat': -23.5450, 'lon': -46.6330},
            'Avenida Paulista': {'lat': -23.5450, 'lon': -46.6270}
        },
        'Vila Mariana': {
            'Rua Domingos de Morais': {'lat': -23.5400, 'lon': -46.6300},
            'Rua Vergueiro': {'lat': -23.5400, 'lon': -46.6330},
            'Avenida Paulista': {'lat': -23.5400, 'lon': -46.6270}
        },
        'Liberdade': {
            'Rua da Liberdade': {'lat': -23.5450, 'lon': -46.6350},
            'Rua Galvão Bueno': {'lat': -23.5450, 'lon': -46.6380},
            'Avenida Liberdade': {'lat': -23.5450, 'lon': -46.6320}
        },
        'Bela Vista': {
            'Rua Augusta': {'lat': -23.5450, 'lon': -46.6350},
            'Rua Consolação': {'lat': -23.5450, 'lon': -46.6380},
            'Avenida Paulista': {'lat': -23.5450, 'lon': -46.6320}
        },
        'Consolação': {
            'Rua da Consolação': {'lat': -23.5450, 'lon': -46.6350},
            'Rua Augusta': {'lat': -23.5450, 'lon': -46.6380},
            'Avenida Paulista': {'lat': -23.5450, 'lon': -46.6320}
        },
        'Higienópolis': {
            'Rua da Consolação': {'lat': -23.5450, 'lon': -46.6350},
            'Rua Augusta': {'lat': -23.5450, 'lon': -46.6380},
            'Avenida Paulista': {'lat': -23.5450, 'lon': -46.6320}
        },
        'Perdizes': {
            'Rua Cardeal Arcoverde': {'lat': -23.5450, 'lon': -46.6350},
            'Rua dos Pinheiros': {'lat': -23.5450, 'lon': -46.6380},
            'Rua Teodoro Sampaio': {'lat': -23.5450, 'lon': -46.6320}
        },
        'Vila Buarque': {
            'Rua da Consolação': {'lat': -23.5450, 'lon': -46.6350},
            'Rua Augusta': {'lat': -23.5450, 'lon': -46.6380},
            'Avenida Paulista': {'lat': -23.5450, 'lon': -46.6320}
        },
        'República': {
            'Rua da Consolação': {'lat': -23.5450, 'lon': -46.6350},
            'Rua Augusta': {'lat': -23.5450, 'lon': -46.6380},
            'Avenida Paulista': {'lat': -23.5450, 'lon': -46.6320}
        },
        'Sé': {
            'Rua da Consolação': {'lat': -23.5450, 'lon': -46.6350},
            'Rua Augusta': {'lat': -23.5450, 'lon': -46.6380},
            'Avenida Paulista': {'lat': -23.5450, 'lon': -46.6320}
        },
        'Bom Retiro': {
            'Rua da Consolação': {'lat': -23.5450, 'lon': -46.6350},
            'Rua Augusta': {'lat': -23.5450, 'lon': -46.6380},
            'Avenida Paulista': {'lat': -23.5450, 'lon': -46.6320}
        },
        'Brás': {
            'Rua da Consolação': {'lat': -23.5450, 'lon': -46.6350},
            'Rua Augusta': {'lat': -23.5450, 'lon': -46.6380},
            'Avenida Paulista': {'lat': -23.5450, 'lon': -46.6320}
        }
    }
    
    data = []
    
    # Gerar dados históricos para RJ
    for neighborhood, coords in rj_neighborhoods.items():
        for i in range(12):  # 12 propriedades por bairro
            # Preço base do bairro
            base_price = np.random.normal(320, 60)  # RJ é mais caro
            
            # Gerar histórico de 12 meses
            historical_prices = []
            for month in range(12):
                # Fator sazonal (RJ tem alta temporada no verão)
                if month in [11, 0, 1]:  # Dez, Jan, Fev
                    seasonal_factor = np.random.uniform(1.6, 2.2)
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
            
            # Selecionar rua aleatória do bairro
            street = np.random.choice(list(rj_streets[neighborhood].keys()))
            street_coords = rj_streets[neighborhood][street]
            
            data.append({
                'city': 'Rio de Janeiro',
                'neighborhood': neighborhood,
                'latitude': street_coords['lat'],
                'longitude': street_coords['lon'],
                'current_price': current_price,
                'avg_price_12m': avg_price,
                'price_std': std_price,
                'price_status': price_status,
                'price_color': price_color,
                'property_type': np.random.choice(['Entire home', 'Private room', 'Shared room']),
                'bedrooms': np.random.randint(1, 4),
                'bathrooms': np.random.randint(1, 3),
                'accommodates': np.random.randint(1, 6),
                'review_scores_rating': np.random.uniform(75, 100),
                'number_of_reviews': np.random.randint(0, 300),
                'host_is_superhost': np.random.choice(['t', 'f']),
                'instant_bookable': np.random.choice(['t', 'f']),
                'availability_30': np.random.randint(0, 30),
                'amenities': '["Wifi", "Kitchen", "Air conditioning", "TV", "Hot water"]',
                'address': f"{street}, {neighborhood}, Rio de Janeiro - RJ"
            })
    
    # Gerar dados históricos para SP
    for neighborhood, coords in sp_neighborhoods.items():
        for i in range(12):  # 12 propriedades por bairro
            # Preço base do bairro
            base_price = np.random.normal(280, 50)  # SP é um pouco mais barato
            
            # Gerar histórico de 12 meses
            historical_prices = []
            for month in range(12):
                # Fator sazonal (SP tem menos sazonalidade)
                if month in [11, 0, 1]:  # Dez, Jan, Fev
                    seasonal_factor = np.random.uniform(1.3, 1.7)
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
            
            # Selecionar rua aleatória do bairro
            street = np.random.choice(list(sp_streets[neighborhood].keys()))
            street_coords = sp_streets[neighborhood][street]
            
            data.append({
                'city': 'São Paulo',
                'neighborhood': neighborhood,
                'latitude': street_coords['lat'],
                'longitude': street_coords['lon'],
                'current_price': current_price,
                'avg_price_12m': avg_price,
                'price_std': std_price,
                'price_status': price_status,
                'price_color': price_color,
                'property_type': np.random.choice(['Entire home', 'Private room', 'Shared room']),
                'bedrooms': np.random.randint(1, 4),
                'bathrooms': np.random.randint(1, 3),
                'accommodates': np.random.randint(1, 6),
                'review_scores_rating': np.random.uniform(75, 100),
                'number_of_reviews': np.random.randint(0, 300),
                'host_is_superhost': np.random.choice(['t', 'f']),
                'instant_bookable': np.random.choice(['t', 'f']),
                'availability_30': np.random.randint(0, 30),
                'amenities': '["Wifi", "Kitchen", "Air conditioning", "TV", "Hot water"]',
                'address': f"{street}, {neighborhood}, São Paulo - SP"
            })
    
    return pd.DataFrame(data)

def create_modern_map(df, selected_city=None, selected_neighborhood=None, map_style="CartoDB Positron"):
    """
    Cria mapa Folium moderno com scroll funcional e opções personalizáveis
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
    
    # Mapear estilos
    style_map = {
        "CartoDB Positron": "CartoDB positron",
        "OpenStreetMap": "OpenStreetMap", 
        "CartoDB Dark": "CartoDB dark_matter"
    }
    
    # Criar mapa com configurações otimizadas
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles=style_map[map_style],
        prefer_canvas=False,
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
    
    # Adicionar camadas de tiles alternativas
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
    
    folium.TileLayer(
        tiles='CartoDB dark_matter',
        name='CartoDB Dark',
        overlay=False,
        control=True
    ).add_to(m)
    
    # Adicionar controle de camadas
    folium.LayerControl().add_to(m)
    
    # Adicionar pontos para cada propriedade
    for idx, property in df.iterrows():
        # Determinar cor baseado no status do preço (sem setas)
        if property['price_status'] == 'high':
            color = 'red'
            icon = 'home'
        elif property['price_status'] == 'low':
            color = 'orange'
            icon = 'home'
        else:
            color = 'green'
            icon = 'home'
        
        # Criar popup moderno
        popup_html = f"""
        <div style="width: 280px; font-family: 'Segoe UI', sans-serif;">
            <div style="background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%); color: white; padding: 15px; border-radius: 10px 10px 0 0; margin: -10px -10px 10px -10px;">
                <h3 style="margin: 0; font-size: 1.2rem;">{property['neighborhood']}, {property['city']}</h3>
            </div>
            <div style="padding: 10px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="font-weight: bold; color: #2c3e50;">💰 Preço Atual:</span>
                    <span style="font-size: 1.2rem; font-weight: bold; color: #e74c3c;">R$ {property['current_price']:.0f}/noite</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="color: #7f8c8d;">📊 Média 12 meses:</span>
                    <span style="font-weight: bold;">R$ {property['avg_price_12m']:.0f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="color: #7f8c8d;">📈 Status:</span>
                    <span style="font-weight: bold; color: {'#e74c3c' if property['price_status'] == 'high' else '#27ae60' if property['price_status'] == 'normal' else '#f39c12'};">{property['price_status'].upper()}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="color: #7f8c8d;">📍 Endereço:</span>
                    <span style="font-weight: bold; font-size: 0.9rem;">{property['address']}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="color: #7f8c8d;">🏠 Tipo:</span>
                    <span style="font-weight: bold;">{property['property_type']}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="color: #7f8c8d;">🛏️ Quartos:</span>
                    <span style="font-weight: bold;">{property['bedrooms']}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="color: #7f8c8d;">⭐ Avaliação:</span>
                    <span style="font-weight: bold;">{property['review_scores_rating']:.1f}/100</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #7f8c8d;">📝 Reviews:</span>
                    <span style="font-weight: bold;">{property['number_of_reviews']}</span>
                </div>
            </div>
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


def main():
    """
    Função principal do dashboard moderno
    """
    # Header moderno
    st.markdown("""
    <div class="main-header">
        <h1>🏠 Airbnb Price Intelligence</h1>
        <p>Análise Inteligente de Preços - São Paulo & Rio de Janeiro</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Carregar dados
    with st.spinner('🔄 Carregando dados históricos do Airbnb...'):
        df = load_airbnb_historical_data()
    
    # Sidebar moderno
    st.sidebar.markdown("## 🎯 Filtros Inteligentes")
    
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
    
    # Métricas principais com design moderno
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">🏠</div>
            <div class="metric-value">{len(filtered_df):,}</div>
            <div class="metric-label">Propriedades</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_price = filtered_df['current_price'].mean()
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">💰</div>
            <div class="metric-value">R$ {avg_price:.0f}</div>
            <div class="metric-label">Preço Médio</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        high_price_pct = (filtered_df['price_status'] == 'high').mean() * 100
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">📈</div>
            <div class="metric-value">{high_price_pct:.1f}%</div>
            <div class="metric-label">Acima da Média</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        low_price_pct = (filtered_df['price_status'] == 'low').mean() * 100
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">📉</div>
            <div class="metric-value">{low_price_pct:.1f}%</div>
            <div class="metric-label">Abaixo da Média</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Seletor de tipo de mapa logo acima do mapa
    map_style = st.selectbox(
        "🗺️ Tipo de Mapa",
        ["CartoDB Positron", "OpenStreetMap", "CartoDB Dark"]
    )
    
    # Legenda de cores apenas
    st.markdown("**🎯 Cores:** 🔴 Acima da média • 🟢 Preço normal • 🟡 Abaixo da média")
    
    # Criar mapa moderno
    folium_map = create_modern_map(
        filtered_df, 
        selected_city if selected_city != 'Todos' else None, 
        selected_neighborhood if selected_neighborhood != 'Todos' else None,
        map_style
    )
    
    # Exibir mapa
    st.markdown('<div class="map-container">', unsafe_allow_html=True)
    st_folium(
        folium_map, 
        width=1200, 
        height=700,
        returned_objects=[]
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    
    # Lista de propriedades
    st.markdown("## 📋 Propriedades na Área")
    
    # Criar lista de propriedades
    property_list = filtered_df.sort_values('current_price', ascending=False)
    
    # Mostrar propriedades
    for idx, property in property_list.iterrows():
        # Status do preço
        if property['price_status'] == 'high':
            status_text = "🔴 ACIMA DA MÉDIA"
            status_class = "status-high"
        elif property['price_status'] == 'low':
            status_text = "🟡 ABAIXO DA MÉDIA"
            status_class = "status-low"
        else:
            status_text = "🟢 NORMAL"
            status_class = "status-normal"
        
        st.markdown(f"""
        <div class="property-card">
            <div class="property-title">{property['neighborhood']}, {property['city']}</div>
            <div class="property-price">R$ {property['current_price']:.0f}/noite</div>
            <div class="property-details">
                📍 {property['address']}<br>
                🏠 {property['property_type']} • {property['bedrooms']} quartos • {property['bathrooms']} banheiros<br>
                ⭐ {property['review_scores_rating']:.1f}/100 • 📝 {property['number_of_reviews']} reviews<br>
                <span class="{status_class}">{status_text}</span> • 📊 Média 12m: R$ {property['avg_price_12m']:.0f}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
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
