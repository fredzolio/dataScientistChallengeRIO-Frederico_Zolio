import streamlit as st
import pandas as pd
import plotly.express as px
from scripts.data_loaders import run_query
from scripts.sql_queries import *
from scripts.api_integration import *
from scripts.visualization import create_map

st.set_page_config(
    page_title="Data Scient. Rio - Frederico Zolio",
    page_icon="🌅"
    )
st.title("Desafio Cientista de Dados Júnior - Prefeitura do Rio de Janeiro")
st.text('Por Frederico Zolio Gonzaga Diniz (fredzolio@live.com)')


# Menu lateral
st.sidebar.title("Menu")
option = st.sidebar.selectbox("Escolha uma seção", ["SQL - Chamados 1746", "Integração com APIs"])

# Seção 1: SQL - Chamados 1746
if option == "SQL - Chamados 1746":
    st.header("Localização de Chamados do 1746")
    
    data = st.date_input("Escolha a data", value=pd.to_datetime("2023-04-01"))
    ##
    st.subheader("1. Quantos chamados foram abertos no dia selecionado?")
    query = query_chamados_abertos_dia(data)
    result = run_query(query)
    st.write(result)
    ##
    st.subheader("2. Qual o tipo de chamado com mais registros?")
    query = query_tipo_mais_chamados_dia(data)
    result = run_query(query)
    st.write(result)
    ##
    st.subheader("3. Quais os 3 bairros com mais chamados?")
    query = query_bairros_mais_chamados_dia(data)
    df_bairros = run_query(query)
    st.write(df_bairros)
    ##
    st.subheader("4. Qual a subprefeitura com mais chamados?")
    query = query_subprefeitura_mais_chamados_dia(data)
    result = run_query(query)
    st.write(result)
    ##
    st.subheader("5. Existem chamados sem bairro ou subprefeitura?")
    query = query_chamados_sem_bairro_subprefeitura(data)
    result = run_query(query)
    st.write(result)
    
    st.info('Isso acontece, devido ao fato de que a categoria desses chamados é: Serviço, e, portanto, o tipo é: Ônibus, caracterizando, assim, uma forma que não depende de uma localidade, e sim de um objeto em manuntenção.')
    ##
    st.header("Chamados do 1746 em Grandes Eventos")
    ##
    st.subheader("6. Quantos chamados com 'Perturbação do sossego' foram abertos entre 01/01/2022 e 31/12/2023?")
    query = query_perturbacao_sossego_chamados("2022-01-01", "2023-12-31")
    result = run_query(query)
    st.write(result)
    ##
    st.subheader("7. Seleção de chamados durante eventos específicos (Reveillon, Carnaval, Rock in Rio)")
    query = query_chamados_durante_eventos()
    df_eventos = run_query(query)
    st.write(df_eventos)
    ##
    st.subheader("8. Quantos chamados foram abertos em cada evento?")
    query = query_chamados_por_evento()
    result = run_query(query)
    st.write(result)
    ##
    st.subheader("9. Qual evento teve a maior média diária de chamados?")
    query = query_media_diaria_por_evento()
    result = run_query(query)
    st.write(result)
    st.info(f"O evento que teve maior média diária de chamados foi: **{result.iloc[0]['evento']}**")
    ##
    st.subheader("10. Comparação das médias diárias de chamados durante os eventos e no período total.")
    query = query_comparacao_media_diaria("2022-01-01", "2023-12-31")
    result = run_query(query)
    st.write(result)
####################
# Seção 2: Integração com APIs
elif option == "Integração com APIs":
    st.header("Integração com APIs: Feriados e Clima")

    year = st.number_input("Ano de escolha", min_value=2024, max_value=2024, value=2024)
    ##
    st.subheader("1. Quantos feriados há no Brasil em 2024?")
    holidays = get_holiday_data(year)
    st.write(f"Total de feriados: {len(holidays)}")
    ##
    st.subheader("2. Qual mês tem o maior número de feriados?")
    holidays_by_month = get_holidays_by_month(holidays)
    st.bar_chart(holidays_by_month, x_label="Meses", y_label="Qtd. de Feriados",)
    ##
    st.subheader("3. Quantos feriados caem em dias úteis?")
    weekdays_holidays = get_holidays_weekdays(holidays)
    st.write(f"Total de feriados em dias úteis: {len(weekdays_holidays)}")
    ##
    st.subheader("4. Qual foi a temperatura média em cada mês? Entre 01/01/2024 e 01/08/2024")
    weather_data = get_weather_data()
    avg_temp_by_month = get_weather_by_month(weather_data)
    fig = px.line(avg_temp_by_month, x='month', y='average_temp', 
                labels={'month': 'Mês', 'average_temp': 'Temperatura Média (°C)'},
                title="Temperatura Média por Mês")
    fig.update_traces(text=avg_temp_by_month['average_temp'].round(2),
                    textposition="top center",
                    mode='lines+markers+text')
    st.plotly_chart(fig)
    ##
    st.subheader("5. Qual foi o tempo predominante em cada mês?")
    weather_data = get_weather_data()
    if 'weather_code' in weather_data.columns:
        predominant_weather = get_weather_code_by_month(weather_data)
        for _, row in predominant_weather.iterrows():
            st.markdown(f"### Mês: {row['month']}")
            st.image(row['image'], width=50)
            st.write(f"Tempo predominante: {row['description']}")
    else:
        st.error("Os dados do código de tempo (weather_code) não estão disponíveis.")
    ##    
    st.subheader("6. Qual foi o tempo e a temperatura média em cada feriado?")
    holidays_weather = get_weather_and_holiday_data(holidays, weather_data)
    holidays_weather = add_weather_description(holidays_weather)
    holidays_weather['holiday_info'] = holidays_weather['localName'] + ' (' + holidays_weather['date'].dt.strftime('%d/%m/%Y') + ')'
    fig = px.line(holidays_weather, x='holiday_info', y='average_temp',
                labels={'holiday_info': 'Feriado', 'average_temp': 'Temperatura Média (°C)'},
                title="Temperatura Média e Tempo Predominante em Cada Feriado")
    fig.update_traces(text=holidays_weather['description'],
                    textposition="top center",
                    mode='lines+markers+text')
    st.plotly_chart(fig)
    ##
    st.subheader("7. Houve algum feriado 'não aproveitável' em 2024?")
    non_enjoyable_weather_codes = [3, 45, 48, 51, 53, 55, 61, 63, 65, 80, 81, 82, 95, 96, 99]
    non_enjoyable_holidays = holidays_weather[
        (holidays_weather['average_temp'] < 20) | 
        (holidays_weather['weather_code'].isin(non_enjoyable_weather_codes))
    ]
    non_enjoyable_holidays['description'] = non_enjoyable_holidays['weather_code'].map(
        lambda code: weather_code_map.get(code, {}).get('description', 'N/A')
    )
    if not non_enjoyable_holidays.empty:
        st.write("Os seguintes feriados foram considerados 'não aproveitáveis' devido ao frio ou mau tempo:")
        st.table(non_enjoyable_holidays[['localName', 'date', 'average_temp', 'description']])
    else:
        st.write("Nenhum feriado foi considerado 'não aproveitável' em 2024.")
    ##
    st.subheader("8. Qual foi o feriado 'mais aproveitável' de 2024?")
    enjoyable_weather_codes = [0, 1, 2]
    enjoyable_holidays = holidays_weather[
        (holidays_weather['average_temp'] >= 20) & 
        (holidays_weather['weather_code'].isin(enjoyable_weather_codes))
    ]
    if not enjoyable_holidays.empty:
        best_holiday = enjoyable_holidays.sort_values(by='average_temp', ascending=False).iloc[0]
        best_holiday['description'] = weather_code_map.get(best_holiday['weather_code'], {}).get('description', 'N/A')
        st.write(f"O feriado mais aproveitável foi: **{best_holiday['localName']}** em {best_holiday['date'].strftime('%d/%m/%Y')}")
        st.write(f"Temperatura média: **{best_holiday['average_temp']}°C**")
        st.write(f"Condição climática: **{best_holiday['description']}**")
    else:
        st.write("Nenhum feriado em 2024 foi considerado 'mais aproveitável'.")