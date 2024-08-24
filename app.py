import calendar
import locale
import streamlit as st
import pandas as pd
import calplot
import plotly.express as px
import plotly.graph_objects as go
from scripts.data_loaders import run_query
from scripts.sql_queries import *
from scripts.api_integration import *
from scripts.visualization import *
from scripts.utils import *

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
option = st.sidebar.selectbox("Escolha uma seção", ["SQL - Chamados 1746", "Integração com APIs"])

# Seção 1: SQL - Chamados 1746
if option == "SQL - Chamados 1746":
    st.header("Localização de Chamados do 1746")
    
    data = st.date_input("Escolha a data", value=pd.to_datetime("2023-04-01"))
    ##
    st.divider()
    st.subheader("1. Quantos chamados foram abertos no dia selecionado?")
    query = query_chamados_abertos_dia(data)
    result = run_query(query)
    result.rename(columns={
        'total_chamados': 'Total de chamados'
        }, inplace=True)
    st.metric("Total de chamados", result['Total de chamados'].iloc[0])
    ##
    st.divider()
    st.subheader("2. Qual o tipo de chamado com mais registros?")
    query = query_tipo_mais_chamados_dia(data)
    result = run_query(query)
    display_metrics(result, 'tipo', 'total')
    ##
    st.divider()
    st.subheader("3. Quais os 3 bairros com mais chamados?")
    query = query_bairros_mais_chamados_dia(data)
    df_bairros = run_query(query)
    gdf_bairros = convert_wkt_to_gdf(df_bairros)
    center_lat, center_lon = get_map_center(gdf_bairros)
    color_scale = [
        [0, "green"],
        [0.5, "blue"],
        [1, "red"]
    ]
    fig = px.choropleth_mapbox(
        gdf_bairros,
        geojson=gdf_bairros.geometry.__geo_interface__,
        locations=gdf_bairros.index,
        color="numero_chamados",
        hover_name="bairro",
        hover_data=["numero_chamados"],
        mapbox_style="carto-positron",
        center={"lat": center_lat, "lon": center_lon},
        zoom=5,
        opacity=0.5,
        color_continuous_scale=color_scale
    )
    for idx, row in gdf_bairros.iterrows():
        fig.add_trace(go.Scattermapbox(
            lat=[row.geometry.centroid.y],
            lon=[row.geometry.centroid.x],
            mode='text',
            text=f"{row['bairro']} ({row['numero_chamados']})",
            textfont=dict(size=14, color="black"),
        ))
    fig.update_layout(
    coloraxis_colorbar=dict(
        title="Número de Chamados",
        tickvals=[60, 70, 80, 90, 100, 110],
        ticktext=['60', '70', '80', '90', '100', '110'],
    ),
    mapbox_zoom=10,
    mapbox_center={"lat": center_lat, "lon": center_lon},
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    showlegend=False
    )
    display_metrics(df_bairros, 'bairro', 'numero_chamados')
    df_bairros.rename(columns={
        'bairro': 'Bairro',
        'numero_chamados': 'Número de chamados'
    }, inplace=True)
    st.info("Mapa em triangulação dos bairros para rápida visualização e identificação.")
    st.plotly_chart(fig, use_container_width=True)
    ##
    st.divider()
    st.subheader("4. Qual a subprefeitura com mais chamados?")
    query = query_subprefeitura_mais_chamados_dia(data)
    result = run_query(query)
    display_metrics(result, 'subprefeitura', 'total')
    ##
    st.divider()
    st.subheader("5. Existem chamados sem bairro ou subprefeitura?")
    query = query_chamados_sem_bairro_subprefeitura(data)
    result = run_query(query)
    result.rename(columns={
        'total':'Total'
    }, inplace=True)
    st.metric('Chamados sem bairro ou subprefeitura',result['Total'].iloc[0])
    st.info('Isso ocorre porque a categoria desses chamados é classificada como "Serviço", e, portanto, o tipo associado é "Ônibus". Isso caracteriza uma situação que não está vinculada a uma localidade específica, mas sim ao objeto em manutenção.')
    ##
    st.divider()
    st.header("Chamados do 1746 em Grandes Eventos")
    ##
    st.divider()
    st.subheader("6. Quantos chamados com 'Perturbação do sossego' foram abertos entre 01/01/2022 e 31/12/2023?")
    query = query_perturbacao_sossego_chamados("2022-01-01", "2023-12-31")
    result = run_query(query)
    result.rename(columns={
        'total':'Total'
    }, inplace=True)
    st.metric('Total',result['Total'].iloc[0])
    ##
    st.divider()
    st.subheader("7. Seleção de chamados durante eventos específicos (Reveillon, Carnaval, Rock in Rio)")
    query = query_chamados_durante_eventos()
    df_eventos = run_query(query)
    st.write(df_eventos)
    ##
    st.divider()
    st.subheader("8. Quantos chamados foram abertos em cada evento?")
    query = query_chamados_por_evento()
    result = run_query(query)
    result.rename(columns={'evento': 'Evento', 'total': 'Total'}, inplace=True)
    display_metrics(result, 'Evento', 'Total')
    chart_type = st.radio("Selecione o tipo de gráfico para visualizar os dados:", ("Barra", "Pizza", "Linha"))
    display_graph(result, chart_type)
    ##
    st.divider()
    st.subheader("9. Qual evento teve a maior média diária de chamados?")
    query = query_media_diaria_por_evento()
    result = run_query(query)
    result.rename(columns={
        'evento': 'Evento',
        'media_diaria':'Média diária'
    }, inplace=True)
    display_metrics(result, 'Evento', 'Média diária')
    st.info(f"O evento que teve maior média diária de chamados foi: **{result.iloc[0]['Evento']}**")
    fig = px.bar(
        result,
        x='Média diária',
        y='Evento',
        orientation='h',
        title="Média Diária de Chamados por Evento",
        height=300,
        width=800
    )
    fig.update_traces(marker=dict(color='blue'), selector=dict(type='bar'))
    st.plotly_chart(fig)
    ##
    st.divider()
    st.subheader("10. Comparação das médias diárias de chamados durante os eventos e no período total.")
    query = query_comparacao_media_diaria("2022-01-01", "2023-12-31")
    result = run_query(query)
    result.rename(columns={
        'evento': 'Evento',
        'media_diaria_evento': 'Média diária do evento',
        'media_diaria_total': 'Média diária total'
    }, inplace=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=result['Evento'],
        y=result['Média diária do evento'],
        name='Média diária do evento',
        marker_color='blue'
    ))
    fig.add_trace(go.Bar(
        x=result['Evento'],
        y=result['Média diária total'],
        name='Média diária total',
        marker_color='orange'
    ))
    fig.update_layout(
        barmode='group',
        title="Comparação das Médias Diárias de Chamados",
        xaxis_title="Evento",
        yaxis_title="Média Diária de Chamados",
        legend_title="Tipo de Média",
        height=400,
        width=800,
        showlegend=True
    )
    st.plotly_chart(fig)
####################
# Seção 2: Integração com APIs
elif option == "Integração com APIs":
    st.header("Integração com APIs: Feriados e Clima")

    year = st.number_input("Ano de escolha", min_value=2024, max_value=2024, value=2024)
    ##
    st.divider()
    st.subheader("1. Quantos feriados há no Brasil em 2024?")
    holidays = get_holiday_data(year)
    st.metric("Total de feriados", len(holidays))
    st.dataframe(holidays[['date', 'localName', 'name']].rename(columns={
    'date': 'Data',
    'localName': 'Feriado (Em nome local)',
    'name': 'Nome Internacional',
    }).style.format({"Data": lambda x: pd.to_datetime(x).strftime('%d/%m/%Y')})
    ,use_container_width=True)
    ##
    st.divider()
    st.subheader("2. Qual mês tem o maior número de feriados?")
    holidays_by_month = get_holidays_by_month(holidays)
    st.bar_chart(holidays_by_month, x_label="Meses", y_label="Qtd. de Feriados",use_container_width=True)
    max_feriados = holidays_by_month.max()
    meses_com_mais_feriados = holidays_by_month[holidays_by_month == max_feriados].index.tolist()
    nomes_meses_com_mais_feriados = [calendar.month_name[mes].capitalize() for mes in meses_com_mais_feriados]
    st.info(f"Os meses com o maior número de feriados ({max_feriados} feriados) são: **{', '.join(nomes_meses_com_mais_feriados)}**.")
    ##
    st.divider()
    st.subheader("3. Quantos feriados caem em dias úteis?")
    weekdays_holidays = get_holidays_weekdays(holidays)
    st.metric("Total de feriados em dias úteis", len(weekdays_holidays))
    weekdays_holidays['count'] = 1
    holidays_calendar = weekdays_holidays.set_index('date').resample('D').sum().fillna(0)
    fig, ax = calplot.calplot(
    holidays_calendar['count'],
    cmap='Reds',
    fillcolor='grey',
    linewidth=0.5,
    textformat='{:.0f}',
    suptitle="Dias Úteis que são Feriados em 2024",
    how="sum",
    )
    st.text("Mapa de calor com os feriados em dia útil.", help="Exploração alternativa aos dias úteis com feriado.")
    st.pyplot(fig)
    ##
    st.divider()
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
    st.divider()
    st.subheader("5. Qual foi o tempo predominante em cada mês?")
    weather_data = get_weather_data()
    if 'weather_code' in weather_data.columns:
        predominant_weather = get_weather_code_by_month(weather_data)
        num_cols = 4
        cols = st.columns(num_cols)
        for i, (_, row) in enumerate(predominant_weather.iterrows()):
            col = cols[i % num_cols]
            with col:
                st.markdown(f"### Mês: {row['month']}")
                st.image(row['image'], width=50)
                st.write(f"Tempo predominante: {row['description']}")
    else:
        st.error("Os dados do código de tempo (weather_code) não estão disponíveis.")
    ##
    st.divider()  
    st.subheader("6. Qual foi o tempo e a temperatura média em cada feriado?")
    view_mode = st.radio(
        "Selecione o modo de visualização:",
        ("Gráfico", "Tabela")
    )
    holidays_weather = get_weather_and_holiday_data(holidays, weather_data)
    holidays_weather = add_weather_description(holidays_weather)
    holidays_weather['holiday_info'] = holidays_weather['localName'] + ' (' + holidays_weather['date'].dt.strftime('%d/%m/%Y') + ')'
    if view_mode == "Gráfico":
        fig = px.line(holidays_weather, x='holiday_info', y='average_temp',
                    labels={'holiday_info': 'Feriado', 'average_temp': 'Temperatura Média (°C)'},
                    title="Temperatura Média e Tempo Predominante em Cada Feriado")
        fig.update_traces(text=holidays_weather['description'],
                        textposition="top center",
                        mode='lines+markers+text')
        st.plotly_chart(fig)
    else:
        st.dataframe(holidays_weather[['holiday_info', 'average_temp', 'description']].rename(columns={
            'holiday_info': 'Feriado',
            'average_temp': 'Temperatura Média (°C)',
            'description': 'Tempo Predominante'
        }))
    ##
    st.divider()
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
        non_enjoyable_holidays['date'] = non_enjoyable_holidays['date'].dt.strftime('%d/%m/%Y')
        st.write("Os seguintes feriados foram considerados 'não aproveitáveis' devido ao frio ou mau tempo:")
        st.table(non_enjoyable_holidays[['localName', 'date', 'average_temp', 'description']].rename(columns={
            'localName': 'Feriado',
            'date': 'Data',
            'average_temp': 'Temp. Média',
            'description': 'Tempo Predom.'
        }))
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
        st.success(f"O feriado mais aproveitável foi: **{best_holiday['localName']}** em {best_holiday['date'].strftime('%d/%m/%Y')}")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Temperatura Média", f"{best_holiday['average_temp']}°C")
        with col2:
            st.image(weather_code_map.get(best_holiday['weather_code'], {}).get('image', ''), width=80)
            st.write(f"Condição Climática: **{best_holiday['description']}**")
        aproveitabilidade = int((best_holiday['average_temp'] - 20) * 5)
        st.text(f"Aproveitabilidade: {aproveitabilidade}%")
        st.progress(aproveitabilidade)
    else:
        st.info("Nenhum feriado em 2024 foi considerado 'mais aproveitável'.")
