import streamlit as st
import plotly.express as px

def display_metrics(result, label_name, value_name):
    cols = st.columns(len(result))
    for idx, row in enumerate(result.iterrows()):
        with cols[idx]:
            value = f"{row[1][value_name]:.2f}"
            st.metric(label=row[1][label_name], value=value)
        
        
def display_graph(result, chart_type):
    if chart_type == "Barra":
        fig = px.bar(result, x='Evento', y='Total', title="Chamados por Evento")
    elif chart_type == "Pizza":
        fig = px.pie(result, names='Evento', values='Total', title="Distribuição de Chamados por Evento")
    elif chart_type == "Linha":
        fig = px.line(result, x='Evento', y='Total', title="Evolução dos Chamados por Evento")
    st.plotly_chart(fig)