import pandas as pd 
import inflection
import io
import re
from haversine import haversine 
import plotly.express as px
import streamlit as st
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static


# Configuração da página
st.set_page_config(
    page_title="Home"
)

#-----------------------------------
### Funções
#-----------------------------------

def rename_columns(dataframe):
    df = dataframe.copy()
    title = lambda x: inflection.titleize(x)
    snakecase = lambda x: inflection.underscore(x)
    spaces = lambda x: x.replace(" ", "")
    cols_old = list(df.columns)
    cols_old = list(map(title, cols_old))
    cols_old = list(map(spaces, cols_old))
    cols_new = list(map(snakecase, cols_old))
    df.columns = cols_new
    return df


COUNTRIES = {
    1: "India",
    14: "Australia",
    30: "Brazil",
    37: "Canada",
    94: "Indonesia",
    148: "New Zeland",
    162: "Philippines",
    166: "Qatar",
    184: "Singapure",
    189: "South Africa",
    191: "Sri Lanka",
    208: "Turkey",
    214: "United Arab Emirates",
    215: "England",
    216: "United States of America"
    }
def country_name(Country_Code):
    return COUNTRIES[Country_Code]

def create_price_tye(price_range):
    if price_range == 1:
        return "cheap"
    elif price_range == 2:
        return "normal"
    elif price_range == 3:
        return "expensive"
    else:
        return "gourmet"

COLORS = {
    "3F7E00": "darkgreen",
    "5BA829": "green",
    "9ACD32": "lightgreen",
    "CDD614": "orange",
    "FFBA00": "red",
    "CBCBC8": "darkred",
    "FF7800": "darkred",
    }
def color_name(color_code):
    return COLORS[color_code]



#-----------------------------------
### Importação dos dados
#-----------------------------------
df = pd.read_csv(r'C:\Users\Thiago\Documents\repos\Projeto_final\dataframe\zomato.csv')

df = rename_columns(df)

df["cuisines"] = df["cuisines"].apply(lambda x: x.split(",")[0] if isinstance(x, str) else x)

df['country'] = df['country_code'].apply(country_name)

df['price_type'] = df['price_range'].apply(create_price_tye)



# =============================================
#Barra lateral
#==============================================


#image_path = 'C:\\Users\\Thiago\\Documents\\repos\\Projeto_final\\target.png'
image = Image.open('target.png')
st.sidebar.image( image,width=120)

st.sidebar.markdown('# Fome Zero')
st.sidebar.markdown("""---""")

# Cabeçalho principal
st.title('Fome Zero!')

# Texto introdutorio
st.header('O Melhor lugar para encontrar seu mais novo restaurante favorito')

st.subheader('Temos as seguintes marcas dentro da nossa plataforma:')

st.sidebar.markdown('## Filtro')
st.sidebar.markdown("""---""")

#Filtro de paises
country_options = st.sidebar.multiselect(
    'Escolha os países que deseja visualizar',
    ['Philippines', 'Brazil', 'Australia', 'United States of America','Canada', 'Singapure', 'United Arab Emirates', 'India','Indonesia', 'New Zeland', 'England', 'Qatar', 'South Africa','Sri Lanka', 'Turkey'],
    default=['Brazil', 'Australia', 'Canada', 'England', 'Qatar', 'South Africa',]
)

st.sidebar.markdown('### Powered by Thiago')

#Filtro de paises
linhas_selecionadas = df['country'].isin(country_options)
df = df.loc[linhas_selecionadas, :]

#python -m streamlit run c:/Users/Thiago/Documents/repos/Projeto_final/Home.py

# =============================================
#layout no Streamlit
#==============================================

tab1, tab2, tab3 = st.tabs (['Countries', 'Cities', 'Cuisines'])
with tab1:
    with st.container():
        col1, col2, col3, col4, col5 = st.columns([4,4,4,4,4], gap = 'small')

        with col1:
            
            qtda_restaurantes = df.loc[:,'restaurant_id'].nunique()
            col1.metric('Restaurantes', qtda_restaurantes)
        
        with col2:
            
            qtda_paises = df.loc[:,'country_code'].nunique()
            col2.metric('Países', qtda_paises)
        
        with col3:
            
            qtda_cidades = df.loc[:,'city'].nunique()
            col3.metric('Cidades', qtda_cidades)
        
        with col4:
            
            qtda_avaliacoes = df.loc[:,'votes'].sum()
            qtda_avaliacoes_mi =  qtda_avaliacoes / 1000000 
            col4.metric('Avaliações',f'{qtda_avaliacoes_mi:.1f} mi')
        
        with col5:
            
            qtda_culinarias = df.loc[:,'cuisines'].nunique()
            col5.metric('Culinárias Oferecidas', qtda_culinarias)

    with st.container():
        country_restaurant_counts = df.groupby('country')['restaurant_id'].nunique().reset_index()

        # Coordenadas aproximadas dos países para plotar os círculos
        country_coordinates = {
            "India": [20.5937, 78.9629],
            "Australia": [-25.2744, 133.7751],
            "Brazil": [-14.2350, -51.9253],
            "Canada": [56.1304, -106.3468],
            "Indonesia": [-0.7893, 113.9213],
            "New Zeland": [-40.9006, 174.8860],
            "Philippines": [12.8797, 121.7740],
            "Qatar": [25.276987, 51.520008],
            "Singapure": [1.3521, 103.8198],
            "South Africa": [-30.5595, 22.9375],
            "Sri Lanka": [7.8731, 80.7718],
            "Turkey": [38.9637, 35.2433],
            "United Arab Emirates": [23.4241, 53.8478],
            "England": [51.5074, -0.1278],
            "United States of America": [37.0902, -95.7129]
        }

        # Criar o mapa centralizado
        map = folium.Map(location=[20, 0], zoom_start=2)
 
        # Adicionar círculos no mapa para cada país
        for _, row in country_restaurant_counts.iterrows():
            country = row['country']
            restaurant_count = row['restaurant_id']
            if country in country_coordinates:
                lat, lon = country_coordinates[country]
                circle_radius = restaurant_count / 10  # Ajustando o tamanho do círculo
                # Adicionar o círculo e a quantidade de restaurantes no popup
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=circle_radius,  # O tamanho do círculo é proporcional ao número de restaurantes
                    color='orange',
                    fill=True,
                    fill_color='orange',
                    fill_opacity=0.6,
                    popup=f"{country}: {restaurant_count} Restaurantes"
                ).add_to(map)

                # Adicionar o número de restaurantes diretamente no mapa
                folium.Marker(
                    location=[lat, lon],
                    popup=f"{restaurant_count} Restaurantes",
                    icon=folium.DivIcon(
                        icon_size=(150,36),
                        icon_anchor=(7, 8),
                        html=f'<div style="font-size: 12pt; color: grey; font-weight: bold;">{restaurant_count}</div>'
                    )
                ).add_to(map)

        # Exibir o mapa no Streamlit
        st.subheader("Mapa de Restaurantes por País")
        folium_static(map, width=700, height=500)