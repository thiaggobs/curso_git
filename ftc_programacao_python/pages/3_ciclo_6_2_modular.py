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
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="3_ciclo_6_2_modular", layout='wide')
#------------------------------------------
#Funções
#------------------------------------------
def distance(df):

        cols = ['Restaurant_latitude','Restaurant_longitude', 'Delivery_location_latitude','Delivery_location_longitude']

        df['distance'] = df.loc[:,cols].apply(lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),(x['Delivery_location_latitude'],x['Delivery_location_longitude'])) , axis=1)

        avg_distancia = np.round(df['distance'].mean())

        return avg_distancia

def avg_time_delivery(df):
        df_aux = (df.loc[:, ['Time_taken(min)', 'Festival']]
                .groupby('Festival')
                .agg( avg_time_delivery = ('Time_taken(min)','mean'), 
                        std_time_delivery = ('Time_taken(min)','std') )
                .reset_index())

        linhas_selecionadas = df_aux['Festival'] =='Yes'
        df_aux = df_aux.reset_index()
        df_aux = np.round(df_aux.loc[linhas_selecionadas,'avg_time_delivery'],2)
        return df_aux

def std_time_delivery(df):
        df_aux = (df.loc[:, ['Time_taken(min)', 'Festival']]
                .groupby('Festival')
                .agg( avg_time_delivery = ('Time_taken(min)','mean'), 
                        std_time_delivery = ('Time_taken(min)','std') )
                .reset_index())
        linhas_selecionadas = df_aux['Festival'] =='Yes'
        df_aux = df_aux.reset_index()
        df_aux = np.round(df_aux.loc[linhas_selecionadas,'std_time_delivery'],2)
        return df_aux
            

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

#==============================================
#Importação dos dados
#==============================================

# Ler o arquivo CSV
df = pd.read_csv("C:/Users/Thiago/Documents/repos/ftc_programacao_python/train.csv")

df = clean_code(df)

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
st.header('Marketplace - Visão Restaurantes')

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



tab1, tab2, tab3 = st.tabs (['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title("Overall Metrics")

        col1, col2, col3, col4, col5, col6 =  st.columns(6)

        with col1:
            
            delivery_unique = df.loc[:, "Delivery_person_ID"].nunique()
            col1.metric ('Entregadores únicos', delivery_unique)

        with col2:
           avg_distancia = distance(df)
           col2.metric ('A distância média das entregas', avg_distancia)
          
        with col3:         
            df_aux = avg_time_delivery(df)
            col3.metric('Tempo médio',df_aux)


        with col4:
            df_aux = std_time_delivery(df)
            col4.metric('STD entrega com Festival',df_aux)          
        
        with col5:
             df_aux = (df.loc[:, ['Time_taken(min)', 'Festival']]
                      .groupby('Festival')
                      .agg( avg_time_delivery = ('Time_taken(min)','mean'), 
                            std_time_delivery = ('Time_taken(min)','std') )
                      .reset_index())
             linhas_selecionadas = df_aux['Festival'] =='No'
             df_aux = df_aux.reset_index()
             df_aux = np.round(df_aux.loc[linhas_selecionadas,'avg_time_delivery'],2)
             col5.metric('Tempo médio',df_aux)
        
        with col6:
             df_aux = (df.loc[:, ['Time_taken(min)', 'Festival']]
                      .groupby('Festival')
                      .agg( avg_time_delivery = ('Time_taken(min)','mean'), 
                            std_time_delivery = ('Time_taken(min)','std') )
                      .reset_index())
             linhas_selecionadas = df_aux['Festival'] =='No'
             df_aux = df_aux.reset_index()
             df_aux = np.round(df_aux.loc[linhas_selecionadas,'std_time_delivery'],2)
             col6.metric('STD entrega com Festival',df_aux)

    with st.container():
       
        cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude','Restaurant_longitude']
        df['distance'] = df.loc[:,cols].apply(lambda x:
                                     haversine ( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                 (x['Delivery_location_latitude'], x['Delivery_location_longitude'])  ), axis=1)
        avg_distancia = df.loc[:, ['City','distance']].groupby('City').mean().reset_index()
        fig = go.Figure(data= [go.Pie(labels=avg_distancia['City'], values=avg_distancia['distance'], pull= [0, 0.1,0])])
        st.plotly_chart (fig)
        


    with st.container():
        st.title("Distribuição do tempo")

        col1, col2 =  st.columns(2)
        with col1:
            st.markdown('#### Coluna1')
        with col2:
            st.markdown('#### Coluna2')

    with st.container():
        st.title("Distribuição da Distância")


#python -m streamlit run c:/Users/Thiago/Documents/repos/ftc_programacao_python/ciclo_6_2.py