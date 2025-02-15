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

def criar_grafico_bar(df, top_10, title, x_label, y_label):
    fig = px.bar(top_10, 
                 x='cuisines', 
                 y='aggregate_rating', 
                 title=title, 
                 labels={'cuisines': x_label, 'aggregate_rating': y_label},
                 color='aggregate_rating',
                 color_continuous_scale='Viridis')
    
    fig.update_layout(
        xaxis_title=x_label,
        yaxis_title=y_label,
        xaxis_tickangle=-45,  # Inclina os rótulos do eixo X para melhor legibilidade
        plot_bgcolor='rgba(0,0,0,0)',  # Torna o fundo do gráfico transparente
        height=400  # Ajuste o tamanho do gráfico para um melhor layout
    )
    return fig


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

#image2_path = 'C:\\Users\\Thiago\\Documents\\repos\\Projeto_final\\cuisine.png'


image2 = Image.open('cuisine.png')

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
        <h1>Visão por tipo de culinária</h1>
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

#python -m streamlit run c:/Users/Thiago/Documents/repos/Projeto_final/Cuisines.py


# =============================================
#layout no Streamlit
#==============================================


st.markdown("""
    <style>
        /* Aumentar o nome da métrica (Título) */
        .metric-title {
            font-size: 18px !important; /* Aumenta o tamanho do nome da métrica */
            font-weight: bold;
        }
        
        /* Reduzir o tamanho do valor da métrica */
        .metric-value {
            font-size: 12px !important; /* Diminui o tamanho do valor exibido */
            color: #2a2a2a;  /* Cor padrão */
            font-style: italic;  /* Deixa o valor em itálico */
        }

        /* Reduzir o espaçamento entre as colunas */
        .css-1d391kg {  /* Classe que controla o espaçamento entre as colunas */
            gap: 10px !important;
        }
    </style>
""", unsafe_allow_html=True)

with st.container():
    st.title('Melhores restaurantes')
    st.markdown("""---""")

    col1, col2, col3, col4, col5 = st.columns(5, gap='small')  # Usando 'small' para reduzir o espaçamento

    with col1:
        media_aval_italiana = df[df['cuisines'] == 'Italian'].groupby('restaurant_name')['aggregate_rating'].mean()
        melhor_avaliado_restaurante_italiano = media_aval_italiana.idxmax()
        col1.markdown(f'<p class="metric-title">Italiano:</p>', unsafe_allow_html=True)
        col1.markdown(f'<p class="metric-value"><i>{melhor_avaliado_restaurante_italiano}</i></p>', unsafe_allow_html=True)

    with col2:
        media_aval_americana = df[df['cuisines'] == 'American'].groupby('restaurant_name')['aggregate_rating'].mean()
        melhor_avaliado_restaurante_americana = media_aval_americana.idxmax()
        col2.markdown(f'<p class="metric-title">Americana:</p>', unsafe_allow_html=True)
        col2.markdown(f'<p class="metric-value"><i>{melhor_avaliado_restaurante_americana}</i></p>', unsafe_allow_html=True)

    with col3:
        media_aval_arabian = df[df['cuisines'] == 'Arabian'].groupby('restaurant_name')['aggregate_rating'].mean()
        melhor_avaliado_restaurante_arabian = media_aval_arabian.idxmax()
        col3.markdown(f'<p class="metric-title">Árabe:</p>', unsafe_allow_html=True)
        col3.markdown(f'<p class="metric-value"><i>{melhor_avaliado_restaurante_arabian}</i></p>', unsafe_allow_html=True)

    with col4:
        media_aval_japanese = df[df['cuisines'] == 'Japanese'].groupby('restaurant_name')['aggregate_rating'].mean()
        melhor_avaliado_restaurante_japanese = media_aval_japanese.idxmax()
        col4.markdown(f'<p class="metric-title">Japonesa:</p>', unsafe_allow_html=True)
        col4.markdown(f'<p class="metric-value"><i>{melhor_avaliado_restaurante_japanese}</i></p>', unsafe_allow_html=True)

    with col5:
        media_aval_caseira = df[df['cuisines'] == 'French'].groupby('restaurant_name')['aggregate_rating'].mean()
        melhor_avaliado_restaurante_caseira = media_aval_caseira.idxmax()
        col5.markdown(f'<p class="metric-title">Francesa:</p>', unsafe_allow_html=True)
        col5.markdown(f'<p class="metric-value"><i>{melhor_avaliado_restaurante_caseira}</i></p>', unsafe_allow_html=True)

with st.container():
        st.markdown("""---""")
        st.subheader('TOP 10 Restaurantes')

        avaliacao_media_restaurantes = df.groupby(['restaurant_id','restaurant_name','country','city','cuisines'])['aggregate_rating'].mean().reset_index()
        top_10_media = avaliacao_media_restaurantes.sort_values('aggregate_rating', ascending=False).head(10)
        st.dataframe(top_10_media)


with st.container():
    st.markdown("""---""")

    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.subheader('TOP 10 Melhores tipos de culinária')
        # Calcular a média das avaliações para cada tipo de culinária
        avaliacao_media_melhores_cusines = df.groupby(['cuisines'])['aggregate_rating'].mean().reset_index()
        # Obter os 10 melhores tipos de culinária
        top_10_media = avaliacao_media_melhores_cusines.sort_values('aggregate_rating', ascending=False).head(10)
        
        # Criar o gráfico
        fig_top_10 = criar_grafico_bar(df, top_10_media, 'Top 10 Melhores Tipos de Culinária', 'Tipo de Culinária', 'Avaliação Média')
        
        # Exibir o gráfico
        st.plotly_chart(fig_top_10)
    
    with col2:
        st.subheader('TOP 10 Piores tipos de culinária')
        # Calcular a média das avaliações para cada tipo de culinária
        avaliacao_media_piores_cusines = df.groupby(['cuisines'])['aggregate_rating'].mean().reset_index()
        # Obter os 10 piores tipos de culinária
        top_10_piores_media = avaliacao_media_piores_cusines.sort_values('aggregate_rating', ascending=True).head(10)
        
        # Criar o gráfico
        fig_top_10_piores = criar_grafico_bar(df, top_10_piores_media, 'Top 10 Piores Tipos de Culinária', 'Tipo de Culinária', 'Avaliação Média')
        
        # Exibir o gráfico
        st.plotly_chart(fig_top_10_piores)