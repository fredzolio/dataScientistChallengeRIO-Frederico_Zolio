import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from scripts.sql_queries import *
from scripts.visualization import *
from scripts.data_loaders import run_query
from scripts.utils import *

@st.cache_data
def render_total_chamados_abertos(data):
    st.subheader("1. Quantos chamados foram abertos no dia selecionado?")
    query = query_chamados_abertos_dia(data)
    result = run_query(query)
    result.rename(columns={'total_chamados': 'Total de chamados'}, inplace=True)
    st.metric("Total de chamados", result['Total de chamados'].iloc[0])
    
@st.cache_data
def render_tipo_mais_chamados(data):
    st.subheader("2. Qual o tipo de chamado com mais registros?")
    query = query_tipo_mais_chamados_dia(data)
    result = run_query(query)
    display_metrics(result, 'tipo', 'total')
    
@st.cache_data
def render_bairros_mais_chamados(data):
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
    
@st.cache_data
def render_subprefeitura_mais_chamados(data):
    st.subheader("4. Qual a subprefeitura com mais chamados?")
    query = query_subprefeitura_mais_chamados_dia(data)
    result = run_query(query)
    display_metrics(result, 'subprefeitura', 'total')
    
@st.cache_data
def render_chamados_sem_bairro(data):
    st.subheader("5. Existem chamados sem bairro ou subprefeitura?")
    query = query_chamados_sem_bairro_subprefeitura(data)
    result = run_query(query)
    result.rename(columns={'total': 'Total'}, inplace=True)
    st.metric('Chamados sem bairro ou subprefeitura', result['Total'].iloc[0])
    st.info('Isso ocorre porque a categoria desses chamados é classificada como "Serviço", e, portanto, o tipo associado é "Ônibus". Isso caracteriza uma situação que não está vinculada a uma localidade específica, mas sim ao objeto em manutenção.')

@st.cache_data
def render_perturbacao_sossego():
    st.subheader("6. Quantos chamados com 'Perturbação do sossego' foram abertos entre 01/01/2022 e 31/12/2023?")
    query = query_perturbacao_sossego_chamados("2022-01-01", "2023-12-31")
    result = run_query(query)
    result.rename(columns={'total': 'Total'}, inplace=True)
    st.metric('Total', result['Total'].iloc[0])
    
@st.cache_data
def render_chamados_durante_eventos():
    st.subheader("7. Seleção de chamados durante eventos específicos (Reveillon, Carnaval, Rock in Rio)")
    query = query_chamados_durante_eventos()
    df_eventos = run_query(query)
    st.write(df_eventos)

def render_chamados_por_evento():
    st.subheader("8. Quantos chamados foram abertos em cada evento?")
    query = query_chamados_por_evento()
    result = run_query(query)
    result.rename(columns={'evento': 'Evento', 'total': 'Total'}, inplace=True)
    display_metrics(result, 'Evento', 'Total')
    chart_type = st.radio("Selecione o tipo de gráfico para visualizar os dados:", ("Barra", "Pizza", "Linha"))
    display_graph(result, chart_type)
    
@st.cache_data
def render_media_diaria_por_evento():
    st.subheader("9. Qual evento teve a maior média diária de chamados?")
    query = query_media_diaria_por_evento()
    result = run_query(query)
    result.rename(columns={'evento': 'Evento', 'media_diaria': 'Média diária'}, inplace=True)
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
    
@st.cache_data
def render_comparacao_media_diaria():
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
