"""
Dashboard moderno para análise de preços do Airbnb - SP & RJ
Refatorado usando Programação Orientada a Objetos (POO)
"""

import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod


class CSSStyler:
    """Gerencia estilos CSS do dashboard"""
    
    @staticmethod
    def get_css() -> str:
        """Retorna CSS completo para o dashboard"""
        return """
        <style>
            * {
                box-sizing: border-box;
            }
            
            .main-header {
                background: #4a4a4a !important;
                color: #ffffff !important;
                padding: 1.5rem;
                border-radius: 8px;
                text-align: center;
                margin-bottom: 1.5rem;
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                border: 1px solid #666666;
            }
            
            .main-header h1 {
                font-size: 2rem;
                font-weight: 600;
                margin: 0;
                color: #ffffff !important;
            }
            
            .main-header p {
                font-size: 1rem;
                margin: 0.5rem 0 0 0;
                color: #cccccc !important;
            }
            
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
            
            .property-card {
                background: #2d2d2d !important;
                border-radius: 8px;
                padding: 1rem;
                margin: 0.5rem 0;
                box-shadow: 0 2px 8px rgba(0,0,0,0.3);
                border: 1px solid #444444;
                transition: all 0.3s ease;
                color: #ffffff !important;
            }
            
            .property-card:hover {
                transform: translateX(5px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.4);
                background: #3d3d3d !important;
            }
            
            .stApp {
                background: #1e1e1e !important;
                color: #ffffff !important;
            }
            
            .stApp * {
                color: #ffffff !important;
            }
            
            h1, h2, h3, h4, h5, h6 {
                color: #ffffff !important;
            }
            
            p, div, span {
                color: #ffffff !important;
            }
            
            .folium-map, .leaflet-container, .leaflet-tile {
                filter: none !important;
                opacity: 1 !important;
            }
        </style>
        """
    
    @staticmethod
    def inject_css():
        """Injeta CSS no Streamlit"""
        st.markdown(CSSStyler.get_css(), unsafe_allow_html=True)


class DataGenerator:
    """Gera dados sintéticos do Airbnb para demo"""
    
    def __init__(self, random_seed: int = 42):
        """
        Args:
            random_seed: Seed para reprodutibilidade
        """
        self.random_seed = random_seed
        np.random.seed(random_seed)
        self._rj_neighborhoods = self._init_rj_neighborhoods()
        self._sp_neighborhoods = self._init_sp_neighborhoods()
        self._rj_streets = self._init_rj_streets()
        self._sp_streets = self._init_sp_streets()
    
    def _init_rj_neighborhoods(self) -> Dict[str, Dict[str, float]]:
        """Inicializa coordenadas de bairros do RJ"""
        return {
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
    
    def _init_sp_neighborhoods(self) -> Dict[str, Dict[str, float]]:
        """Inicializa coordenadas de bairros de SP"""
        return {
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
    
    def _init_rj_streets(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Inicializa ruas por bairro do RJ"""
        return {
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
            }
        }
    
    def _init_sp_streets(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Inicializa ruas por bairro de SP"""
        return {
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
            }
        }
    
    def _generate_property_data(self, city: str, neighborhood: str, 
                                base_price: float, streets: Dict) -> List[Dict]:
        """Gera dados para propriedades de um bairro"""
        data = []
        streets_for_neighborhood = streets.get(neighborhood, {})
        if not streets_for_neighborhood:
            return data
        
        for i in range(12):  # 12 propriedades por bairro
            historical_prices = self._generate_historical_prices(base_price, city)
            avg_price = np.mean(historical_prices)
            std_price = np.std(historical_prices)
            current_price = historical_prices[-1]
            
            price_status, price_color = self._classify_price_status(
                current_price, avg_price, std_price
            )
            
            street = np.random.choice(list(streets_for_neighborhood.keys()))
            street_coords = streets_for_neighborhood[street]
            
            data.append({
                'city': city,
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
                'address': f"{street}, {neighborhood}, {city}"
            })
        
        return data
    
    def _generate_historical_prices(self, base_price: float, city: str) -> List[float]:
        """Gera histórico de preços de 12 meses"""
        historical_prices = []
        for month in range(12):
            if city == 'Rio de Janeiro':
                if month in [11, 0, 1]:  # Dez, Jan, Fev
                    seasonal_factor = np.random.uniform(1.6, 2.2)
                elif month in [2, 3, 4]:  # Mar, Abr, Mai
                    seasonal_factor = np.random.uniform(0.8, 1.2)
                else:
                    seasonal_factor = np.random.uniform(0.9, 1.3)
            else:  # São Paulo
                if month in [11, 0, 1]:
                    seasonal_factor = np.random.uniform(1.3, 1.7)
                else:
                    seasonal_factor = np.random.uniform(0.9, 1.2)
            
            price = base_price * seasonal_factor
            historical_prices.append(price)
        
        return historical_prices
    
    def _classify_price_status(self, current_price: float, avg_price: float, 
                               std_price: float) -> Tuple[str, str]:
        """Classifica status do preço"""
        if current_price > avg_price + std_price:
            return 'high', 'red'
        elif current_price < avg_price - std_price:
            return 'low', 'orange'
        else:
            return 'normal', 'green'
    
    @st.cache_data
    def generate_data(_self) -> pd.DataFrame:
        """Gera DataFrame completo com dados do Airbnb"""
        data = []
        
        # RJ
        for neighborhood in _self._rj_neighborhoods.keys():
            base_price = np.random.normal(320, 60)
            data.extend(_self._generate_property_data(
                'Rio de Janeiro', neighborhood, base_price, _self._rj_streets
            ))
        
        # SP
        for neighborhood in _self._sp_neighborhoods.keys():
            base_price = np.random.normal(280, 50)
            data.extend(_self._generate_property_data(
                'São Paulo', neighborhood, base_price, _self._sp_streets
            ))
        
        return pd.DataFrame(data)


class MapCreator:
    """Cria mapas interativos com Folium"""
    
    MAP_STYLES = {
        "Normal (Ruas)": {
            "tiles": "OpenStreetMap",
            "attr": "OpenStreetMap contributors"
        },
        "Google Maps": {
            "tiles": "CartoDB positron",
            "attr": "CartoDB"
        },
        "Escuro (Dark)": {
            "tiles": "CartoDB dark_matter",
            "attr": "CartoDB"
        }
    }
    
    CITY_CENTERS = {
        'São Paulo': (-23.5505, -46.6333),
        'Rio de Janeiro': (-22.9068, -43.1729)
    }
    
    def __init__(self):
        self.default_center = self.CITY_CENTERS['Rio de Janeiro']
    
    def create_map(self, df: pd.DataFrame, selected_city: Optional[str] = None,
                   selected_neighborhood: Optional[str] = None,
                   map_style: str = "Google Maps") -> folium.Map:
        """
        Cria mapa Folium com propriedades
        
        Args:
            df: DataFrame com dados das propriedades
            selected_city: Cidade selecionada
            selected_neighborhood: Bairro selecionado
            map_style: Estilo do mapa
        
        Returns:
            Mapa Folium configurado
        """
        filtered_df = self._filter_data(df, selected_city, selected_neighborhood)
        center = self._get_center(selected_city)
        
        style_config = self.MAP_STYLES.get(map_style, self.MAP_STYLES["Google Maps"])
        
        m = folium.Map(
            location=center,
            zoom_start=12,
            tiles=style_config["tiles"],
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
        
        # Limpar e adicionar layer
        m._children.clear()
        folium.TileLayer(
            tiles=style_config["tiles"],
            name=map_style,
            overlay=False,
            attr=style_config["attr"]
        ).add_to(m)
        
        # Adicionar marcadores
        for idx, property in filtered_df.iterrows():
            self._add_marker(m, property)
        
        return m
    
    def _filter_data(self, df: pd.DataFrame, selected_city: Optional[str],
                     selected_neighborhood: Optional[str]) -> pd.DataFrame:
        """Filtra DataFrame baseado em cidade e bairro"""
        filtered = df.copy()
        if selected_city:
            filtered = filtered[filtered['city'] == selected_city]
        if selected_neighborhood:
            filtered = filtered[filtered['neighborhood'] == selected_neighborhood]
        return filtered
    
    def _get_center(self, selected_city: Optional[str]) -> Tuple[float, float]:
        """Retorna coordenadas do centro baseado na cidade"""
        if selected_city in self.CITY_CENTERS:
            return self.CITY_CENTERS[selected_city]
        return self.default_center
    
    def _add_marker(self, map_obj: folium.Map, property: pd.Series):
        """Adiciona marcador ao mapa"""
        color = 'red' if property['price_status'] == 'high' else \
                'orange' if property['price_status'] == 'low' else 'green'
        
        popup_html = self._create_popup_html(property)
        
        folium.Marker(
            location=[property['latitude'], property['longitude']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{property['neighborhood']} - R$ {property['current_price']:.0f}",
            icon=folium.Icon(color=color, icon='home', prefix='fa')
        ).add_to(map_obj)
    
    def _create_popup_html(self, property: pd.Series) -> str:
        """Cria HTML para popup do marcador"""
        status_color = '#ff6b6b' if property['price_status'] == 'high' else \
                      '#4ecdc4' if property['price_status'] == 'normal' else '#f9ca24'
        
        return f"""
        <div style="width: 280px; font-family: 'Segoe UI', sans-serif;">
            <div style="background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%); 
                        color: white; padding: 15px; border-radius: 10px 10px 0 0; 
                        margin: -10px -10px 10px -10px;">
                <h3 style="margin: 0; font-size: 1.2rem;">{property['neighborhood']}, {property['city']}</h3>
            </div>
            <div style="padding: 10px; background: #2d2d2d; border-radius: 0 0 10px 10px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="font-weight: bold; color: #ffffff;">💰 Preço Atual:</span>
                    <span style="font-size: 1.2rem; font-weight: bold; color: #ff6b6b;">R$ {property['current_price']:.0f}/noite</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="color: #cccccc;">📊 Média 12 meses:</span>
                    <span style="font-weight: bold; color: #ffffff;">R$ {property['avg_price_12m']:.0f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="color: #cccccc;">📈 Status:</span>
                    <span style="font-weight: bold; color: {status_color};">{property['price_status'].upper()}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="color: #cccccc;">📍 Endereço:</span>
                    <span style="font-weight: bold; font-size: 0.9rem; color: #ffffff;">{property['address']}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="color: #cccccc;">🏠 Tipo:</span>
                    <span style="font-weight: bold; color: #ffffff;">{property['property_type']}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="color: #cccccc;">🛏️ Quartos:</span>
                    <span style="font-weight: bold; color: #ffffff;">{property['bedrooms']}</span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <span style="color: #cccccc;">⭐ Avaliação:</span>
                    <span style="font-weight: bold; color: #ffffff;">{property['review_scores_rating']:.1f}/100</span>
                </div>
                <div style="display: flex; justify-content: space-between;">
                    <span style="color: #cccccc;">📝 Reviews:</span>
                    <span style="font-weight: bold; color: #ffffff;">{property['number_of_reviews']}</span>
                </div>
            </div>
        </div>
        """


class DashboardRenderer:
    """Renderiza componentes do dashboard"""
    
    @staticmethod
    def render_header():
        """Renderiza cabeçalho do dashboard"""
        st.markdown("""
        <div class="main-header" style="background: #4a4a4a !important; color: #ffffff !important; border: 1px solid #666666;">
            <h1 style="color: #ffffff !important; font-size: 2rem; font-weight: 600; margin: 0;">🏠 Airbnb Price Intelligence</h1>
            <p style="color: #cccccc !important; font-size: 1rem; margin: 0.5rem 0 0 0;">Análise Inteligente de Preços - São Paulo & Rio de Janeiro</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_metrics(filtered_df: pd.DataFrame):
        """Renderiza métricas principais"""
        avg_price = filtered_df['current_price'].mean()
        high_price_pct = (filtered_df['price_status'] == 'high').mean() * 100
        low_price_pct = (filtered_df['price_status'] == 'low').mean() * 100
        
        st.markdown(f"""
        <div style="display: flex; gap: 8px; margin: 5px 0;">
            <div style="background: #2d2d2d; padding: 1rem; border-radius: 8px; flex: 1; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.3); border: 1px solid #444444;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🏠</div>
                <div style="font-size: 1.5rem; font-weight: bold; color: #ffffff;">{len(filtered_df):,}</div>
                <div style="font-size: 0.9rem; color: #cccccc;">Propriedades</div>
            </div>
            <div style="background: #2d2d2d; padding: 1rem; border-radius: 8px; flex: 1; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.3); border: 1px solid #444444;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">💰</div>
                <div style="font-size: 1.5rem; font-weight: bold; color: #ffffff;">R$ {avg_price:.0f}</div>
                <div style="font-size: 0.9rem; color: #cccccc;">Preço Médio</div>
            </div>
            <div style="background: #2d2d2d; padding: 1rem; border-radius: 8px; flex: 1; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.3); border: 1px solid #444444;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📈</div>
                <div style="font-size: 1.5rem; font-weight: bold; color: #ffffff;">{high_price_pct:.1f}%</div>
                <div style="font-size: 0.9rem; color: #cccccc;">Acima da Média</div>
            </div>
            <div style="background: #2d2d2d; padding: 1rem; border-radius: 8px; flex: 1; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.3); border: 1px solid #444444;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">📉</div>
                <div style="font-size: 1.5rem; font-weight: bold; color: #ffffff;">{low_price_pct:.1f}%</div>
                <div style="font-size: 0.9rem; color: #cccccc;">Abaixo da Média</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_properties(filtered_df: pd.DataFrame):
        """Renderiza lista de propriedades"""
        st.markdown("## 📋 Propriedades na Área")
        property_list = filtered_df.sort_values('current_price', ascending=False)
        
        for idx, property in property_list.iterrows():
            status_text, status_class = DashboardRenderer._get_status_info(
                property['price_status']
            )
            
            st.markdown(f"""
            <div class="property-card" style="background: #2d2d2d !important; color: #ffffff !important; border: 1px solid #444444;">
                <div class="property-title" style="color: #ffffff !important; font-weight: bold; font-size: 1.2rem; margin-bottom: 0.5rem;">{property['neighborhood']}, {property['city']}</div>
                <div class="property-price" style="color: #ff6b6b !important; font-size: 1.5rem; font-weight: bold; margin-bottom: 0.8rem;">R$ {property['current_price']:.0f}/noite</div>
                <div class="property-details" style="color: #cccccc !important; line-height: 1.6;">
                    📍 <span style="color: #ffffff !important;">{property['address']}</span><br>
                    🏠 <span style="color: #ffffff !important;">{property['property_type']}</span> • <span style="color: #ffffff !important;">{property['bedrooms']} quartos</span> • <span style="color: #ffffff !important;">{property['bathrooms']} banheiros</span><br>
                    ⭐ <span style="color: #ffffff !important;">{property['review_scores_rating']:.1f}/100</span> • 📝 <span style="color: #ffffff !important;">{property['number_of_reviews']} reviews</span><br>
                    <span class="{status_class}" style="font-weight: bold;">{status_text}</span> • 📊 Média 12m: <span style="color: #ffffff !important;">R$ {property['avg_price_12m']:.0f}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    @staticmethod
    def _get_status_info(price_status: str) -> Tuple[str, str]:
        """Retorna texto e classe CSS para status do preço"""
        status_map = {
            'high': ('🔴 ACIMA DA MÉDIA', 'status-high'),
            'low': ('🟡 ABAIXO DA MÉDIA', 'status-low'),
            'normal': ('🟢 NORMAL', 'status-normal')
        }
        return status_map.get(price_status, ('🟢 NORMAL', 'status-normal'))
    
    @staticmethod
    def render_info():
        """Renderiza informações sobre a análise"""
        st.markdown("## ℹ️ Sobre a Análise")
        st.info("""
        **📊 Análise de Preços dos Últimos 12 Meses:**
        
        - **🔴 Acima da Média**: Preço atual > média + desvio padrão
        - **🟢 Normal**: Preço atual dentro da faixa normal
        - **🟡 Abaixo da Média**: Preço atual < média - desvio padrão
        
        **🎯 Objetivo**: Identificar oportunidades de investimento e momentos de preço ideal
        """)


class AirbnbDashboardApp:
    """Classe principal do dashboard"""
    
    def __init__(self):
        """Inicializa componentes do dashboard"""
        self.css_styler = CSSStyler()
        self.data_generator = DataGenerator()
        self.map_creator = MapCreator()
        self.renderer = DashboardRenderer()
        self._setup_page()
    
    def _setup_page(self):
        """Configura página do Streamlit"""
        st.set_page_config(
            page_title="🏠 Airbnb Price Intelligence - SP & RJ",
            page_icon="🏠",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        self.css_styler.inject_css()
    
    def run(self):
        """Executa o dashboard"""
        self.renderer.render_header()
        
        # Carregar dados
        with st.spinner('🔄 Carregando dados históricos do Airbnb...'):
            df = self.data_generator.generate_data()
        
        # Sidebar
        self._render_sidebar(df)
        
        # Filtrar dados
        filtered_df = self._apply_filters(df)
        
        # Renderizar métricas
        self.renderer.render_metrics(filtered_df)
        
        # Mapa
        self._render_map(filtered_df)
        
        # Propriedades
        self.renderer.render_properties(filtered_df)
        
        # Informações
        self.renderer.render_info()
    
    def _render_sidebar(self, df: pd.DataFrame):
        """Renderiza sidebar com filtros"""
        st.sidebar.markdown("## 🎯 Filtros Inteligentes")
        
        cities = ['Todos'] + sorted(df['city'].unique().tolist())
        selected_city = st.sidebar.selectbox("🏙️ Cidade", cities)
        
        if selected_city != 'Todos':
            neighborhoods = ['Todos'] + sorted(
                df[df['city'] == selected_city]['neighborhood'].unique().tolist()
            )
        else:
            neighborhoods = ['Todos'] + sorted(df['neighborhood'].unique().tolist())
        
        selected_neighborhood = st.sidebar.selectbox("🏘️ Bairro", neighborhoods)
        
        # Armazenar seleções
        st.session_state.selected_city = selected_city
        st.session_state.selected_neighborhood = selected_neighborhood
    
    def _apply_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica filtros selecionados"""
        filtered = df.copy()
        
        selected_city = st.session_state.get('selected_city', 'Todos')
        selected_neighborhood = st.session_state.get('selected_neighborhood', 'Todos')
        
        if selected_city != 'Todos':
            filtered = filtered[filtered['city'] == selected_city]
        if selected_neighborhood != 'Todos':
            filtered = filtered[filtered['neighborhood'] == selected_neighborhood]
        
        return filtered
    
    def _render_map(self, filtered_df: pd.DataFrame):
        """Renderiza mapa interativo"""
        map_style = st.selectbox(
            "🗺️ Tipo de Mapa",
            ["Normal (Ruas)", "Google Maps", "Escuro (Dark)"]
        )
        
        st.markdown("**🎯 Cores:** 🔴 Acima da média • 🟢 Preço normal • 🟡 Abaixo da média")
        
        selected_city = st.session_state.get('selected_city', 'Todos')
        selected_neighborhood = st.session_state.get('selected_neighborhood', 'Todos')
        
        folium_map = self.map_creator.create_map(
            filtered_df,
            selected_city if selected_city != 'Todos' else None,
            selected_neighborhood if selected_neighborhood != 'Todos' else None,
            map_style
        )
        
        st.markdown('<div class="map-container">', unsafe_allow_html=True)
        st_folium(folium_map, width=1200, height=700, returned_objects=[])
        st.markdown('</div>', unsafe_allow_html=True)


def main():
    """Função principal"""
    app = AirbnbDashboardApp()
    app.run()


if __name__ == "__main__":
    main()