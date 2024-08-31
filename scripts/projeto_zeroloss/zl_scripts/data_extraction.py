import os
import sys

import pandas as pd
import requests

sys.path.append(os.path.abspath(os.curdir))

from scripts.data_loaders import run_query

def get_dados_estacoes():
    query = """
    SELECT 
        id_estacao, 
        estacao, 
        latitude, 
        longitude, 
        cota, 
        x, 
        y, 
        endereco, 
        situacao, 
        data_inicio_operacao, 
        data_fim_operacao, 
        data_atualizacao 
    FROM `datario.clima_pluviometro.estacoes_alertario`
    """
    
    df_estacoes = run_query(query)
    return df_estacoes

def get_previsao_meteorologica(latitude, longitude):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,precipitation,cloudcover"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['hourly']
    else:
        return None

def get_dados_precipitacao_com_previsao():
    query = """
    SELECT 
        id_estacao, 
        acumulado_chuva_15_min, 
        acumulado_chuva_1_h, 
        acumulado_chuva_4_h, 
        acumulado_chuva_24_h, 
        acumulado_chuva_96_h, 
        horario, 
        data_particao
    FROM `datario.clima_pluviometro.taxa_precipitacao_alertario`
    ORDER BY data_particao DESC, horario DESC
    LIMIT 10
    """
    
    df_precipitacao = run_query(query)

    df_estacoes = get_dados_estacoes()

    df_precipitacao = pd.merge(df_precipitacao, df_estacoes[['id_estacao', 'latitude', 'longitude']], on='id_estacao')

    df_precipitacao['previsao_meteorologica'] = df_precipitacao.apply(
        lambda row: get_previsao_meteorologica(row['latitude'], row['longitude']), axis=1)

    return df_precipitacao
