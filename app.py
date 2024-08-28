import streamlit as st
from scripts.dialogflow_integration import detect_intent_from_text
from scripts.render_sql import *
from scripts.render_api import *

set_locale_to_pt_br()

st.set_page_config(
    page_title="Data Scient. Rio - Frederico Zolio",
    page_icon="🌅",
    layout="wide"
    )
st.title("Desafio Cientista de Dados Júnior - Prefeitura do Rio de Janeiro")
st.caption('Por Frederico Zolio Gonzaga Diniz (fredzolio@live.com)')


# Menu lateral
st.sidebar.title("Menu")
option = st.sidebar.selectbox("Escolha uma seção", ["SQL - Chamados 1746", "Integração com APIs", "Assistente Virtual"])

# Seção 1: SQL - Chamados 1746
if option == "SQL - Chamados 1746":
    st.header("Localização de Chamados do 1746")
    
    data = st.date_input("Escolha a data", value=pd.to_datetime("2023-04-01"))
    ##
    st.divider()
    render_total_chamados_abertos(data)
    st.divider()
    render_tipo_mais_chamados(data)
    st.divider()
    render_bairros_mais_chamados(data)
    st.divider()
    render_subprefeitura_mais_chamados(data)
    st.divider()
    render_chamados_sem_bairro(data)
    st.divider()
    render_perturbacao_sossego()
    st.divider()
    render_chamados_durante_eventos()
    st.divider()
    render_chamados_por_evento()
    st.divider()
    render_media_diaria_por_evento()
    st.divider()
    render_comparacao_media_diaria()
    st.divider()
####################
# Seção 2: Integração com APIs
elif option == "Integração com APIs":
    st.header("Integração com APIs: Feriados e Clima")
    
    year = st.number_input("Ano de escolha", min_value=2024, max_value=2024, value=2024)
    holidays = get_holiday_data(year)
    weather_data = get_weather_data()
    holidays_weather = get_weather_and_holiday_data(holidays, weather_data)
    holidays_weather = add_weather_description(holidays_weather)
    ##
    st.divider()
    render_total_feriados(year)
    st.divider()
    render_feriados_por_mes(holidays)
    st.divider()
    render_feriados_dias_uteis(holidays)
    st.divider()
    render_temperatura_media_por_mes()
    st.divider()
    render_tempo_predominante_por_mes()
    st.divider()
    render_tempo_e_temp_media_feriados(holidays, weather_data)
    st.divider()
    render_feriados_nao_aproveitaveis(holidays_weather)
    st.divider()
    render_feriado_mais_aproveitavel(holidays_weather)
    st.divider()
########################
# Seção 3: Assistente Fred
elif option == "Assistente Virtual":
    st.header("Assistente Virtual")
    st.subheader("Converse com o Fred, nosso assistente virtual capaz de responder suas dúvidas acerca do desafio.")
    user_input = st.text_input("Pergunte algo sobre os chamados ou feriados:")
    if user_input:
        response = detect_intent_from_text(user_input, session_id="123456")
        st.write(f"<span style='color: lightgreen; font-weight: bold;'>Fred (Assistente Data Rio):</span> {response}", unsafe_allow_html=True)
########################
