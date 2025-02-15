#Libraies
import pandas as pd
import io
import re
from haversine import haversine 
import plotly.express as px
import streamlit as st
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title="2_ciclo_6_1_modular", layout='wide')
#------------------------------------------
#Funções
#------------------------------------------


def clean_code(df):
    """Está função tem a responsabilidade de limpar o dataframe
       
       Tipos de limpeza:
       1.Remoção dos dados NAN
       2.Mudança do tipo da coluna
       3.Remoção dos espaços das variáveis de texto
       4.Formatação da coluna datas
       5. Limpeza da coluna de tempo
       Input: Dataframe
       Output: Dataframe
    """

    # Remover linhas onde a idade do entregador é NaN
    linhas_selecionadas = df["Delivery_person_Age"].notna()
    df = df.loc[linhas_selecionadas, :].copy()

    # Remover linhas onde a Cidade é em branco
    linhas_selecionadas = (df["City"] !='NaN ')
    df = df.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df["Festival"] !='NaN ')
    df = df.loc[linhas_selecionadas, :].copy()

    # Converter a idade do entregador para numérico, lidando com erros
    df["Delivery_person_Age"] = pd.to_numeric(df["Delivery_person_Age"], errors='coerce')

    # Remover linhas com NaN após conversão
    df = df[df["Delivery_person_Age"].notna()]

    # Converter a idade do entregador para inteiro
    df["Delivery_person_Age"] = df["Delivery_person_Age"].astype(int)

    # Converter as classificações dos entregadores para float, lidando com erros
    df["Delivery_person_Ratings"] = pd.to_numeric(df['Delivery_person_Ratings'], errors='coerce')
    df = df[df["Delivery_person_Ratings"].notna()]  # Remover linhas com NaN

    # Converter a data do pedido para datetime
    df["Order_Date"] = pd.to_datetime(df['Order_Date'], format='%d-%m-%Y')

    # Remover linhas onde o número de entregas múltiplas é NaN
    linhas_selecionadas = df['multiple_deliveries'].notna()
    df = df.loc[linhas_selecionadas, :].copy()

    # Converter múltiplas entregas para inteiro, lidando com erros
    df['multiple_deliveries'] = pd.to_numeric(df['multiple_deliveries'], errors='coerce')
    df = df[df['multiple_deliveries'].notna()]  # Remover linhas com NaN

    # Converter múltiplas entregas para inteiro
    df['multiple_deliveries'] = df['multiple_deliveries'].astype(int)

    df.loc[:, 'ID'] = df.loc[:, 'ID'].str.strip()
    df.loc[:, 'Road_traffic_density'] = df.loc[:, 'Road_traffic_density'].str.strip()
    df.loc[:, 'Type_of_order'] = df.loc[:, 'Type_of_order'].str.strip()
    df.loc[:, 'Type_of_vehicle'] = df.loc[:, 'Type_of_vehicle'].str.strip()
    df.loc[:, 'City'] = df.loc[:, 'City'].str.strip()
    df.loc[:, 'Festival'] = df.loc[:, 'Festival'].str.strip()

    #limpando a coluna time taken

    df['Time_taken(min)'] = df['Time_taken(min)'].apply(lambda x: x.split('(min)')[1])
    df['Time_taken(min)'] = df['Time_taken(min)'].astype(int)

    return df

# Ler o arquivo CSV
df = pd.read_csv("C:/Users/Thiago/Documents/repos/ftc_programacao_python/train.csv")

df = clean_code(df)


# Exibir a forma do DataFrame
print(df)

# =============================================
#Barra lateral
#==============================================


#image_path = 'C:\\Users\\Thiago\\Documents\\repos\\ftc_programacao_python\\logo.png'
image = Image.open('ftc_programacao_python\logo.png')
st.sidebar.image( image,width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Entrega Mais Rápida da Cidade')
st.sidebar.markdown("""---""")

# Cabeçalho principal
st.header('Marketplace - Visão Entregadores')

# Barra lateral - Seleção de data
st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor',
    value=datetime(2022, 4, 6),
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 13),
    format='DD-MM-YYYY'
)

# Exibe a data selecionada
st.write(f'Selecionou a data: {date_slider.strftime("%d-%m-%Y")}')

st.sidebar.markdown("""---""")


traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)

st.sidebar.markdown("""---""")

st.sidebar.markdown('### Powered by Thiago')

#Filtro de data
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas, :]

#Filtro de trânsito
linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas, :]

# =============================================
#layout no Streamlit
#==============================================

#python -m streamlit run c:/Users/Thiago/Documents/repos/ftc_programacao_python/ciclo_6_1.py

tab1, tab2, tab3 = st.tabs (['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])
with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4, gap = 'large')

        with col1:
            
            maior_idade = df.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior de idade', maior_idade)

        with col2:
            
            menor_idade = df.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)

        with col3:
            
            melhor_veiculo = df.loc[:, 'Vehicle_condition'].max()
            col3.metric('A melhor condição ', melhor_veiculo)
        with col4:
            
            pior_veiculo = df.loc[:, 'Vehicle_condition'].min()
            col4.metric('A pior condição', pior_veiculo)

    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')

        col1, col2 = st.columns (2)
        with col1:
            st.subheader('Avaliação média por entregador')
            df_avg_ratings_per_deliver = (df.loc[:,['Delivery_person_Ratings','Delivery_person_ID']]
                                          .groupby('Delivery_person_ID')
                                          .mean()
                                          .reset_index())
            st.dataframe(df_avg_ratings_per_deliver)


        with col2:
            st.subheader('Avaliação média por trânsito')
            df_avg_std_rating_by_traffic = (df.loc[:,['Delivery_person_Ratings','Road_traffic_density']]
                                            .groupby('Road_traffic_density')
                                            .agg( delivery_mean = ('Delivery_person_Ratings','mean'),
                                                  delivery_std= ('Delivery_person_Ratings', 'std'))
                                            .reset_index())
            st.dataframe(df_avg_std_rating_by_traffic)                  

            st.subheader('Avaliação média por clima')
            df_avg_std_rating_by_weather = (df.loc[:,['Delivery_person_Ratings','Weatherconditions']]
                                            .groupby('Weatherconditions')
                                            .agg( delivery_mean = ('Delivery_person_Ratings','mean'), 
                                                    delivery_std= ('Delivery_person_Ratings', 'std'))
                                            .reset_index())
            st.dataframe(df_avg_std_rating_by_weather)

    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de Entrega')
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Top Entregadores mais rápidos')
            df1= (df.loc[:,['Delivery_person_ID','Time_taken(min)','City']]
                    .groupby(['City','Delivery_person_ID'])
                    .min()
                    .sort_values(['City','Time_taken(min)']).reset_index())
            st.dataframe(df1)
            
        with col2:
            st.subheader ('Top Entregadores mais lentos')
            df1= (df.loc[:,['Delivery_person_ID','Time_taken(min)','City']]
                    .groupby(['City','Delivery_person_ID'])
                    .max()
                    .sort_values(['City','Time_taken(min)']).reset_index())
            st.dataframe(df1)