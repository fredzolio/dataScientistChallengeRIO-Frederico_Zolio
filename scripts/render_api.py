import numpy as np
import streamlit as st
import calendar
import plotly.express as px
from scripts.api_integration import *

def render_total_feriados(year):
    st.subheader("1. Quantos feriados há no Brasil em 2024?")
    holidays = get_holiday_data(year)
    st.metric("Total de feriados", len(holidays))
    st.dataframe(holidays[['date', 'localName', 'name']].rename(columns={
        'date': 'Data',
        'localName': 'Feriado (Em nome local)',
        'name': 'Nome Internacional',
    }).style.format({"Data": lambda x: pd.to_datetime(x).strftime('%d/%m/%Y')}), use_container_width=True)

def render_feriados_por_mes(holidays):
    st.subheader("2. Qual mês tem o maior número de feriados?")
    holidays_by_month = get_holidays_by_month(holidays)
    st.bar_chart(holidays_by_month, use_container_width=True)
    max_feriados = holidays_by_month.max()
    meses_com_mais_feriados = holidays_by_month[holidays_by_month == max_feriados].index.tolist()
    nomes_meses_com_mais_feriados = [calendar.month_name[mes].capitalize() for mes in meses_com_mais_feriados]
    st.info(f"Os meses com o maior número de feriados ({max_feriados} feriados) são: **{', '.join(nomes_meses_com_mais_feriados)}**.")

def render_feriados_dias_uteis(holidays):
    st.subheader("3. Quantos feriados caem em dias úteis?")
    weekdays_holidays = get_holidays_weekdays(holidays)
    st.metric("Total de feriados em dias úteis", len(weekdays_holidays))
    weekdays_holidays['date_str'] = weekdays_holidays['date'].dt.strftime('%Y-%m-%d')
    weekdays_holidays['dia_semana'] = weekdays_holidays['date'].dt.strftime('%A')
    weekdays_trad = {
        'Monday': 'Segunda-feira',
        'Tuesday': 'Terça-feira',
        'Wednesday': 'Quarta-feira',
        'Thursday': 'Quinta-feira',
        'Friday': 'Sexta-feira',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }
    weekdays_holidays['dia_semana'] = weekdays_holidays['dia_semana'].replace(weekdays_trad)
    weekdays_holidays['y_pos'] = np.arange(len(weekdays_holidays))
    fig = px.scatter(weekdays_holidays, x='date', y='y_pos',
                    title="Feriados em Dias Úteis",
                    labels={'date': 'Data', 'localName': 'Feriado', 'y_pos': ''},
                    hover_data={'date_str': True,},
                    height=400)
    
    fig.update_traces(marker=dict(size=20, color='red'), 
                    selector=dict(mode='markers'),
                    hovertemplate="<b>%{customdata[0]}</b><br>Data: %{x|%d-%b-%Y}<br>Dia da Semana: %{customdata[1]}<extra></extra>",
                    customdata=np.stack((weekdays_holidays['localName'], weekdays_holidays['dia_semana']), axis=-1))
    
    fig.update_layout(showlegend=False)
    fig.update_layout(
        xaxis=dict(
            showgrid=True,
            tickmode='linear',
            tick0=weekdays_holidays['date'].min(),
            dtick="M1",
            tickformat="%d-%b"
        ),
        yaxis=dict(showticklabels=False),
        margin={"r": 0, "t": 0, "l": 0, "b": 0}
    )
    st.plotly_chart(fig, use_container_width=True)

def render_temperatura_media_por_mes():
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

def render_tempo_predominante_por_mes():
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

def render_tempo_e_temp_media_feriados(holidays, weather_data):
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

def render_feriados_nao_aproveitaveis(holidays_weather):
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
        non_enjoyable_holidays['month'] = non_enjoyable_holidays['date'].dt.strftime('%B')
        non_enjoyable_holidays['temp_type'] = non_enjoyable_holidays['average_temp'].apply(
            lambda temp: 'Frio' if temp < 20 else 'Mau Tempo'
        )
        
        view_option = st.radio(
            "Escolha o modo de visualização:",
            ("Tabela", "Gráfico Radar")
        )
        
        if view_option == "Tabela":
            st.write("Os seguintes feriados foram considerados 'não aproveitáveis' devido ao frio ou mau tempo:")
            # Tabela
            st.dataframe(non_enjoyable_holidays[['localName', 'date', 'average_temp', 'description']].rename(columns={
                'localName': 'Feriado',
                'date': 'Data',
                'average_temp': 'Temp. Média',
                'description': 'Tempo Predom.'
            }))
        else:
            monthly_summary = non_enjoyable_holidays.groupby('month').agg({
                'localName': 'count',
                'average_temp': 'mean'
            }).reset_index()
            monthly_summary.columns = ['Mês', 'Total Feriados', 'Temp. Média']
            monthly_summary['Tipo de Clima'] = monthly_summary['Temp. Média'].apply(
                lambda temp: 'Frio' if temp < 20 else 'Mau Tempo'
            )
            
            # Radar
            fig = px.line_polar(monthly_summary, r='Total Feriados', theta='Mês', 
                                line_close=True, 
                                color='Tipo de Clima',
                                hover_name='Mês',
                                hover_data={'Temp. Média': ':.2f'},
                                title="Distribuição dos Feriados 'Não Aproveitáveis' ao Longo do Ano",
                                template="plotly_dark")
            fig.update_traces(fill='toself')
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("Nenhum feriado foi considerado 'não aproveitável' em 2024.")

def render_feriado_mais_aproveitavel(holidays_weather):
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
