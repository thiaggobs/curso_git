
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

# Ler o arquivo CSV
df = pd.read_csv("C:/Users/Thiago/Documents/repos/ftc_programacao_python/train.csv")

print (df.head())

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


# Exibir a forma do DataFrame
print(df)


#Visao empresa

#1.Quantidade de pedidos por dia

cols = ['ID', 'Order_Date']

df_aux = df.loc[:, cols].groupby('Order_Date').count().reset_index()

px.bar( df_aux, x= 'Order_Date', y='ID')

# =============================================
#Barra lateral
#==============================================


image_path = 'C:\\Users\\Thiago\\Documents\\repos\\ftc_programacao_python\\logo.png'
image = Image.open(image_path)
st.sidebar.image( image,width=120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Entrega Mais Rápida da Cidade')
st.sidebar.markdown("""---""")

# Cabeçalho principal
st.header('Marketplace - Visão Cliente')

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

#python -m streamlit run c:/Users/Thiago/Documents/repos/ftc_programacao_python/ciclo_6.py

tab1, tab2, tab3 = st.tabs (['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        #Order Metric

        st.markdown ('# Orders by Day')
        cols = ['ID', 'Order_Date']
        df_aux = df.loc[:, cols].groupby('Order_Date').count().reset_index()
        fig = px.bar( df_aux, x= 'Order_Date', y='ID')
        st.plotly_chart(fig, use_container_width=True)

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.header('Traffic Order Share')
            df_aux = df.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
            df_aux = df_aux.loc[df_aux['Road_traffic_density'] != "NaN", :]
            df_aux['entregas_perc'] =df_aux['ID']/df_aux['ID'].sum()
            fig = px.pie(df_aux, values='entregas_perc', names='Road_traffic_density')
            st.plotly_chart( fig, se_container_width=True )


        with col2:
            st.header('Traffic Order City')
            df_aux = df.loc[:,['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
            df_aux  = df_aux.loc[df_aux['City'] != 'NaN', :]
            df_aux  = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN', :]
            fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
            st.plotly_chart( fig, se_container_width=True )
  
with tab2:
  with st.container():
    df['Order_Date'] = pd.to_datetime(df['Order_Date'])

    # Criar a coluna 'week_of_year' (semana do ano)
    df['week_of_year'] = df['Order_Date'].dt.strftime('%U')  # %U retorna o número da semana do ano (domingo)

    # Verificar se a coluna 'week_of_year' foi criada corretamente
    print(df[['Order_Date', 'week_of_year']].head())

    # 1. Número de pedidos por semana (contagem de 'ID')
    df_aux_1 = df.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()

    # 2. Número único de entregadores por semana
    df_aux_2 = df.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()

    # 3. Juntar os DataFrames com o merge
    df_aux = pd.merge(df_aux_1, df_aux_2, on='week_of_year', how='inner')

    # 4. Calcular a quantidade média de pedidos por entregador por semana
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']

    # 5. Criar o gráfico de linha
    fig = px.line(df_aux, x='week_of_year', y='order_by_deliver', title='Pedidos por Entregador por Semana')
    st.plotly_chart( fig, se_container_width=True )
 

with tab3:
    st.markdown('# Country Maps')
    df_aux = df.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()
    df_aux = df_aux.loc[df_aux['City']!= 'NaN', :]
    df_aux = df_aux.loc[df_aux['Road_traffic_density']!= 'NaN', :]

    map = folium.Map()

    for index, location_info in df_aux.iterrows():
      folium.Marker([location_info['Delivery_location_latitude'], 
                    location_info['Delivery_location_longitude']]).add_to(map)

    folium_static(map, width=1024 , height=600)


