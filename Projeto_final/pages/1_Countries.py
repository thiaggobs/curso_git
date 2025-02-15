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


def image2_to_base64(image):
    import base64
    from io import BytesIO
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


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

#image2_path = 'C:\\Users\\Thiago\\Documents\\repos\\Projeto_final\\map.png'
image2 = Image.open('map.png')

st.sidebar.image( image,width=120)

# Cabeçalho principal

st.markdown(
    f"""
    <style>
    .header {{
        display: flex;
        align-items: center;
    }}
    .header img {{
        margin-right: 10px;
        width: 45px;
    }}
    .header h1 {{
        margin: 0;
    }}
    </style>
    <div class="header">
        <img src="data:image/png;base64,{image2_to_base64(image2)}" alt="Logo">
        <h1>Visão Países</h1>
    </div>
    """,
    unsafe_allow_html=True
)


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

#python -m streamlit run c:/Users/Thiago/Documents/repos/Projeto_final/Countries.py

# =============================================
#layout no Streamlit
#==============================================



with st.container():
    #Order Metric
    qtda_restaurantes_pais = df.groupby('country')['restaurant_id'].count().reset_index()
    qtda_restaurantes_pais = qtda_restaurantes_pais.sort_values('restaurant_id', ascending=False)
    fig = px.bar( qtda_restaurantes_pais, x= 'country', y='restaurant_id', labels={'restaurant_id': 'Quantidade de Restaurantes'}, title='Quantidade de Restaurantes Registrados por País',text='restaurant_id')
    st.plotly_chart(fig, use_container_width=True)

with st.container():

    qtda_cidades_pais = df.groupby('country')['city'].nunique().reset_index()
    qtda_cidades_pais = qtda_cidades_pais.sort_values('city', ascending=False)
    fig = px.bar( qtda_cidades_pais, x= 'country', y='city', labels={'city': 'Quantidade de Cidades'}, title='Quantidade de Cidades Registrados por País',text='city')
    st.plotly_chart(fig, use_container_width=True)

with st.container():
    
    col1, col2 = st.columns([1,1], gap = 'small')

    with col1:
        media_avaliacoes_pais = df.groupby('country')['votes'].mean().reset_index()
        media_avaliacoes_pais['votes'] = media_avaliacoes_pais['votes'].round(2)
        media_avaliacoes_pais = media_avaliacoes_pais.sort_values('votes', ascending=False)
        fig = px.bar( media_avaliacoes_pais, x= 'country', y='votes', labels={'votes': 'Quantidade de avaliações'}, title='Média de Avaliações por País',text='votes')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        media_preco_duas_pais = df.groupby('country')['average_cost_for_two'].mean().reset_index()
        media_preco_duas_pais['average_cost_for_two'] = media_preco_duas_pais['average_cost_for_two'].round(2)
        media_preco_duas_pais = media_preco_duas_pais.sort_values('average_cost_for_two', ascending=False)
        fig = px.bar( media_preco_duas_pais, x= 'country', y='average_cost_for_two', labels={'average_cost_for_two': 'Preço médio para duas pessoas'}, title='Preço médio para duas pessoas por País',text='average_cost_for_two')
        st.plotly_chart(fig, use_container_width=True)