import os
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib
from tqdm import tqdm

from .data_extraction import get_dados_estacoes, get_dados_precipitacao_com_previsao

def preparar_dados():
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
    
    df = df.dropna(subset=['acumulado_chuva_1_h'])
    
    X = df.drop(columns=['acumulado_chuva_1_h'])
    y = df['acumulado_chuva_1_h']
    
    feature_names = X.columns.tolist()

    return train_test_split(X, y, test_size=0.2, random_state=42), feature_names

def treinar_e_salvar_modelo():
    print("Iniciando preparação de dados...")
    (X_train, X_test, y_train, y_test), feature_names = preparar_dados()
    print("Dados preparados. Iniciando treinamento...")
    
    n_estimators = 100
    model = RandomForestRegressor(n_estimators=n_estimators, random_state=42, warm_start=True)
    
    for i in tqdm(range(1, n_estimators + 1), desc="Treinando o modelo"):
        model.n_estimators = i
        model.fit(X_train, y_train)
    
    print("Treinamento concluído. Salvando o modelo...")
    
    if not os.path.exists('modelos'):
        os.makedirs('modelos')
    
    joblib.dump((model, feature_names), "modelos/modelo_precipitacao.pkl")
    print("Modelo salvo com sucesso em 'modelos/modelo_precipitacao.pkl'.")

if __name__ == "__main__":
    treinar_e_salvar_modelo()
