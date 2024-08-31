import joblib
import streamlit as st
import pandas as pd
from .data_extraction import get_dados_estacoes, get_dados_precipitacao_com_previsao
from .visualization import exibir_mapa_calor

@st.cache_data
def preparar_dados_para_previsao(feature_names):
    df_estacoes = get_dados_estacoes()
    df_precipitacao = get_dados_precipitacao_com_previsao()
    df = pd.merge(df_precipitacao, df_estacoes, on='id_estacao')
    df['data_particao'] = pd.to_datetime(df['data_particao'])
    df['horario'] = pd.to_datetime(df['horario'].astype(str))
    
    df['data_particao'] = df['data_particao'].apply(lambda x: x.timestamp())
    df['horario'] = df['horario'].apply(lambda x: x.timestamp())

    if 'previsao_meteorologica' in df.columns:
        df['media_temperatura'] = df['previsao_meteorologica'].apply(lambda x: sum(x['temperature_2m']) / len(x['temperature_2m']))
        df['max_precipitacao'] = df['previsao_meteorologica'].apply(lambda x: max(x['precipitation']))
        df['media_nuvens'] = df['previsao_meteorologica'].apply(lambda x: sum(x['cloudcover']) / len(x['cloudcover']))
        df = df.drop(columns=['previsao_meteorologica'])

    df = df.drop(columns=['id_estacao', 'estacao', 'endereco', 'situacao', 
                        'data_inicio_operacao', 'data_fim_operacao', 'data_atualizacao'])

    X = df[feature_names]
    
    return X

@st.cache_data
def render_ml_modelo():
    print("Carregando modelo salvo...")
    modelo, feature_names = joblib.load("modelos/modelo_precipitacao.pkl")
    
    print("Preparando dados para previsão...")
    X_test = preparar_dados_para_previsao(feature_names)
    
    print("Fazendo previsões...")
    previsoes = modelo.predict(X_test)
    df_resultado = X_test.copy()
    df_resultado['previsao_chuva_1_h'] = previsoes
    
    print("Resultados das previsões:")
    print(df_resultado.head())
    
    fig = exibir_mapa_calor(df_resultado, 'previsao_chuva_1_h')
    st.plotly_chart(fig, use_container_width=True)