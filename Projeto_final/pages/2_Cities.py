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

#image2_path = 'C:\\Users\\Thiago\\Documents\\repos\\Projeto_final\\city.png'

image2 = Image.open('city.png')

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
        <h1>Visão Cidades</h1>
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

#python -m streamlit run c:/Users/Thiago/Documents/repos/Projeto_final/Cities.py

# =============================================
#layout no Streamlit
#==============================================



with st.container():
    qtda_restaurantes_cidades = df.groupby(['city', 'country'])['restaurant_id'].count().reset_index()
    qtda_restaurantes_cidades = qtda_restaurantes_cidades.sort_values('restaurant_id', ascending=False)
    qtda_restaurantes_cidades_top = qtda_restaurantes_cidades.head(10)

    # Criando o gráfico com cores diferentes para cada país
    fig = px.bar(qtda_restaurantes_cidades_top, 
                x='city', 
                y='restaurant_id', 
                color='country',  # Define a cor com base na coluna 'country'
                labels={'restaurant_id': 'Quantidade de Restaurantes'}, 
                title='Top 10 Cidades com mais restaurantes', 
                text='restaurant_id')

    # Exibindo o gráfico
    st.plotly_chart(fig, use_container_width=True)

with st.container():
    qtda_restaurantes_cidades_melhores = df.groupby(['city','restaurant_id', 'country'])['votes'].mean().reset_index()
    qtda_restaurantes_cidades_melhores = qtda_restaurantes_cidades_melhores[qtda_restaurantes_cidades_melhores['votes'] > 50]
    qtda_restaurantes_cidades_top_ava = qtda_restaurantes_cidades_melhores.groupby(['city','country'])['restaurant_id'].count().reset_index()
    qtda_restaurantes_cidades_top_ava = qtda_restaurantes_cidades_top_ava.sort_values('restaurant_id', ascending=False)
    qtda_restaurantes_cidades_top_ava = qtda_restaurantes_cidades_top_ava[qtda_restaurantes_cidades_top_ava['restaurant_id'] > 50]
    
    # Criando o gráfico com cores diferentes para cada país
    fig = px.bar(qtda_restaurantes_cidades_top_ava, 
                x='city', 
                y='restaurant_id', 
                color='country',  # Define a cor com base na coluna 'country'
                labels={'restaurant_id': 'Quantidade de Restaurantes'}, 
                title='QTDA restaurantes por cidade com avaliação média acima de 50', 
                text='restaurant_id')

    # Exibindo o gráfico
    st.plotly_chart(fig, use_container_width=True)

with st.container():
    qtda_restaurantes_cidades_piores = df.groupby(['city','restaurant_id', 'country'])['votes'].mean().reset_index()
    qtda_restaurantes_cidades_piores = qtda_restaurantes_cidades_piores[qtda_restaurantes_cidades_piores['votes'] < 50]
    qtda_restaurantes_cidades_down_ava = qtda_restaurantes_cidades_melhores.groupby(['city','country'])['restaurant_id'].count().reset_index()
    qtda_restaurantes_cidades_down_ava = qtda_restaurantes_cidades_down_ava.sort_values('restaurant_id', ascending=False)
    qtda_restaurantes_cidades_down_ava = qtda_restaurantes_cidades_down_ava[qtda_restaurantes_cidades_down_ava['restaurant_id'] > 50]
    
    # Criando o gráfico com cores diferentes para cada país
    fig = px.bar(qtda_restaurantes_cidades_down_ava, 
                x='city', 
                y='restaurant_id', 
                color='country',  # Define a cor com base na coluna 'country'
                labels={'restaurant_id': 'Quantidade de Restaurantes'}, 
                title='QTDA restaurantes por cidade com avaliação média abaixo de 50', 
                text='restaurant_id')

    # Exibindo o gráfico
    st.plotly_chart(fig, use_container_width=True)    

with st.container():
    qtda_restaurantes_cidades_cusines = df.groupby(['city','restaurant_id', 'country'])['cuisines'].count().reset_index()
    qtda_restaurantes_cidades_cusines = qtda_restaurantes_cidades_cusines[qtda_restaurantes_cidades_cusines['cuisines'] > 1]
    qtda_restaurantes_cidades_top_cusines = qtda_restaurantes_cidades_cusines.groupby(['city','country'])['restaurant_id'].count().reset_index()
    qtda_restaurantes_cidades_top_cusines = qtda_restaurantes_cidades_top_cusines.sort_values('restaurant_id', ascending=False)
    qtda_restaurantes_cidades_top_cusines = qtda_restaurantes_cidades_top_cusines[qtda_restaurantes_cidades_top_cusines['restaurant_id'] > 10]

    # Criando o gráfico com cores diferentes para cada país
    fig = px.bar(qtda_restaurantes_cidades_top_cusines, 
                x='city', 
                y='restaurant_id', 
                color='country',  # Define a cor com base na coluna 'country'
                labels={'restaurant_id': 'Quantidade de Restaurantes'}, 
                title='QTDA restaurantes por cidade com diversas culinárias', 
                text='restaurant_id')

    # Exibindo o gráfico
    st.plotly_chart(fig, use_container_width=True)    