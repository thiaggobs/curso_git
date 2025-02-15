import streamlit as st
from PIL import Image

# Configuração da página
st.set_page_config(
    page_title="Home"
)

# Caminho da imagem
#image_path = 'C:\\Users\\Thiago\\Documents\\repos\\ftc_programacao_python\\logo.png'
image = Image.open('ftc_programacao_python\logo.png')

# Exibir a imagem no sidebar
st.sidebar.image(image, width=120)

# Conteúdo do sidebar
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Entrega Mais Rápida da Cidade')
st.sidebar.markdown("""---""")

# Título principal
st.write('# Curry Company Growth Dashboard')

# Descrição do dashboard
st.markdown(
    """
    Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    
    ### Como utilizar esse Growth Dashboard?
    
    - **Visão Empresa:**
        - Visão Geral: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
        
    - **Visão Entregador:**
        - Acompanhamento dos indicadores semanais de crescimento.
        
    - **Visão Restaurante:**
        - Indicadores semanais de crescimento dos restaurantes.
    """
)

###python -m streamlit run c:/Users/Thiago/Documents/repos/ftc_programacao_python/Home.py