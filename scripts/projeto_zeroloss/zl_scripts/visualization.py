import plotly.express as px

def exibir_mapa_calor(df, coluna_valor):
    fig = px.density_mapbox(df, lat='latitude_x', lon='longitude_x', z=coluna_valor, radius=10,
                            center=dict(lat=-22.9068, lon=-43.1729), zoom=10,
                            mapbox_style="carto-positron")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    return fig