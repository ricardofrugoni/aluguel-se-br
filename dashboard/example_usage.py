"""
Exemplo de uso do dashboard de análise de preços de aluguel.
Demonstra como integrar o dashboard com dados reais.
"""

import pandas as pd
import numpy as np
import streamlit as st
from pathlib import Path
import sys

# Adicionar o diretório pai ao path para importar módulos
sys.path.append(str(Path(__file__).parent.parent))

from src.features.temporal_features import TemporalFeatureEngineer
from src.features.review_features import ReviewFeatureEngineer
from src.features.amenity_features import AmenityFeatureEngineer
from config import AMENITY_CATEGORIES, MIN_REVIEWS_FOR_TRUST, MAJOR_HOLIDAYS

def create_sample_data():
    """
    Cria dados de exemplo mais realistas para o dashboard.
    """
    np.random.seed(42)
    
    # Dados baseados em padrões reais do Airbnb
    cities = ['São Paulo', 'Rio de Janeiro']
    property_types = ['Entire home', 'Private room', 'Shared room']
    
    data = []
    
    for city in cities:
        for prop_type in property_types:
            # Parâmetros baseados no tipo de propriedade
            if prop_type == 'Entire home':
                base_price = np.random.normal(200, 80) if city == 'Rio de Janeiro' else np.random.normal(150, 60)
                bedrooms = np.random.choice([1, 2, 3, 4], p=[0.4, 0.3, 0.2, 0.1])
            elif prop_type == 'Private room':
                base_price = np.random.normal(80, 30) if city == 'Rio de Janeiro' else np.random.normal(60, 25)
                bedrooms = 1
            else:  # Shared room
                base_price = np.random.normal(40, 15) if city == 'Rio de Janeiro' else np.random.normal(30, 12)
                bedrooms = 1
            
            for i in range(100):  # Mais propriedades por categoria
                # Features temporais
                temporal_engineer = TemporalFeatureEngineer(holidays=MAJOR_HOLIDAYS)
                
                # Features de review
                review_engineer = ReviewFeatureEngineer(min_reviews=MIN_REVIEWS_FOR_TRUST)
                
                # Features de amenidades
                amenity_engineer = AmenityFeatureEngineer(amenity_categories=AMENITY_CATEGORIES)
                
                # Dados base
                property_data = {
                    'id': f"{city}_{prop_type}_{i}",
                    'city': city,
                    'property_type': prop_type,
                    'price': max(base_price + np.random.normal(0, base_price * 0.2), 20),
                    'latitude': np.random.uniform(-23.8, -23.3) if city == 'São Paulo' else np.random.uniform(-23.1, -22.8),
                    'longitude': np.random.uniform(-46.8, -46.3) if city == 'São Paulo' else np.random.uniform(-43.4, -43.1),
                    'bedrooms': bedrooms,
                    'bathrooms': np.random.randint(1, min(bedrooms + 1, 3)),
                    'review_scores_rating': np.random.uniform(4.0, 5.0) * 20,
                    'number_of_reviews': np.random.poisson(20),
                    'reviews_per_month': np.random.uniform(0.5, 3.0),
                    'host_is_superhost': np.random.choice(['t', 'f'], p=[0.3, 0.7]),
                    'host_identity_verified': np.random.choice(['t', 'f'], p=[0.8, 0.2]),
                    'host_response_rate': f"{np.random.randint(80, 101)}%",
                    'host_acceptance_rate': f"{np.random.randint(70, 101)}%",
                    'host_listings_count': np.random.randint(1, 10),
                    'host_since': pd.to_datetime('2020-01-01') + pd.Timedelta(days=np.random.randint(0, 1460)),
                    'availability_30': np.random.randint(0, 31),
                    'availability_60': np.random.randint(0, 61),
                    'availability_90': np.random.randint(0, 91),
                    'amenities': '["Wifi", "Kitchen", "Air conditioning", "TV", "Cable TV", "Hot water"]'
                }
                
                # Adicionar variação sazonal ao preço
                month = np.random.randint(1, 13)
                if city == 'Rio de Janeiro':
                    seasonal_factors = [1.5, 1.6, 1.2, 1.0, 0.9, 0.85, 0.9, 0.95, 1.0, 1.1, 1.2, 1.7]
                else:
                    seasonal_factors = [1.3, 1.2, 1.0, 0.95, 0.9, 0.9, 1.2, 0.95, 1.0, 1.1, 1.1, 1.4]
                
                property_data['price'] *= seasonal_factors[month - 1]
                property_data['current_month'] = month
                
                data.append(property_data)
    
    return pd.DataFrame(data)

def demonstrate_seasonal_analysis():
    """
    Demonstra a análise sazonal com dados reais.
    """
    st.markdown("## 🎯 Demonstração de Análise Sazonal")
    
    # Criar dados de exemplo
    df = create_sample_data()
    
    # Selecionar uma propriedade
    selected_property = df.sample(1).iloc[0]
    
    st.markdown(f"### Propriedade Selecionada: {selected_property['city']} - {selected_property['property_type']}")
    
    # Gerar análise sazonal
    temporal_engineer = TemporalFeatureEngineer(holidays=MAJOR_HOLIDAYS)
    
    # Criar DataFrame temporário para análise
    temp_df = pd.DataFrame([selected_property])
    temp_df['current_date'] = pd.to_datetime('today')
    
    # Adicionar features temporais
    featured_df = temporal_engineer.add_all_temporal_features(temp_df)
    
    # Mostrar resultados
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Preço Base", f"R$ {selected_property['price']:.2f}")
    
    with col2:
        if 'season' in featured_df.columns:
            st.metric("Estação", featured_df['season'].iloc[0])
    
    with col3:
        if 'is_high_season' in featured_df.columns:
            st.metric("Alta Temporada", "Sim" if featured_df['is_high_season'].iloc[0] else "Não")
    
    # Análise de amenidades
    st.markdown("### 🏠 Análise de Amenidades")
    
    amenity_engineer = AmenityFeatureEngineer(amenity_categories=AMENITY_CATEGORIES)
    amenity_df = amenity_engineer.add_amenity_features(temp_df)
    
    if 'amenity_score' in amenity_df.columns:
        st.metric("Amenity Score", f"{amenity_df['amenity_score'].iloc[0]:.2f}")
    
    # Análise de reviews
    st.markdown("### ⭐ Análise de Reviews")
    
    review_engineer = ReviewFeatureEngineer(min_reviews=MIN_REVIEWS_FOR_TRUST)
    review_df = review_engineer.add_all_review_features(temp_df)
    
    if 'trust_score' in review_df.columns:
        st.metric("Trust Score", f"{review_df['trust_score'].iloc[0]:.2f}")
    
    if 'host_quality_score' in review_df.columns:
        st.metric("Host Quality Score", f"{review_df['host_quality_score'].iloc[0]:.2f}")

def demonstrate_market_analysis():
    """
    Demonstra análise de mercado.
    """
    st.markdown("## 📊 Análise de Mercado")
    
    # Criar dados de exemplo
    df = create_sample_data()
    
    # Métricas gerais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Propriedades", len(df))
    
    with col2:
        st.metric("Preço Médio", f"R$ {df['price'].mean():.2f}")
    
    with col3:
        st.metric("Rating Médio", f"{df['review_scores_rating'].mean():.1f}")
    
    with col4:
        superhosts = len(df[df['host_is_superhost'] == 't'])
        st.metric("Superhosts", f"{superhosts} ({superhosts/len(df)*100:.1f}%)")
    
    # Análise por cidade
    st.markdown("### 🏙️ Análise por Cidade")
    
    city_analysis = df.groupby('city').agg({
        'price': ['mean', 'std', 'min', 'max'],
        'review_scores_rating': 'mean',
        'number_of_reviews': 'mean'
    }).round(2)
    
    st.dataframe(city_analysis)
    
    # Análise por tipo de propriedade
    st.markdown("### 🏠 Análise por Tipo de Propriedade")
    
    type_analysis = df.groupby('property_type').agg({
        'price': ['mean', 'std', 'min', 'max'],
        'review_scores_rating': 'mean',
        'number_of_reviews': 'mean'
    }).round(2)
    
    st.dataframe(type_analysis)

def main():
    """
    Função principal do exemplo.
    """
    st.set_page_config(
        page_title="Dashboard Example",
        page_icon="🏠",
        layout="wide"
    )
    
    st.title("🏠 Exemplo de Uso do Dashboard")
    st.markdown("Demonstração das funcionalidades do dashboard com dados simulados.")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs([
        "🎯 Análise Sazonal",
        "📊 Análise de Mercado", 
        "🔧 Configurações"
    ])
    
    with tab1:
        demonstrate_seasonal_analysis()
    
    with tab2:
        demonstrate_market_analysis()
    
    with tab3:
        st.markdown("### ⚙️ Configurações do Dashboard")
        
        st.markdown("#### Categorias de Amenidades")
        st.json(AMENITY_CATEGORIES)
        
        st.markdown("#### Feriados Brasileiros")
        st.write(MAJOR_HOLIDAYS)
        
        st.markdown("#### Configurações de Review")
        st.metric("Mínimo de Reviews para Confiança", MIN_REVIEWS_FOR_TRUST)
        
        # Botão para executar dashboard completo
        if st.button("🚀 Executar Dashboard Completo"):
            st.info("Para executar o dashboard completo, use: `streamlit run dashboard/globe_app.py`")

if __name__ == "__main__":
    main()
