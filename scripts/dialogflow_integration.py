from google.cloud import dialogflow_v2 as dialogflow
from google.oauth2 import service_account
import toml
from scripts.render_sql import *
from scripts.render_api import *

def load_credentials_toml(file_path='.streamlit\secrets.toml'):
    config = toml.load(file_path)
    credentials_info = config['dialogflow']
    credentials = service_account.Credentials.from_service_account_info(credentials_info)
    return credentials

def detect_intent_from_text(text, session_id, language_code='pt-BR'):
    credentials = load_credentials_toml('.streamlit/secrets.toml')
    session_client = dialogflow.SessionsClient(credentials=credentials)
    session = session_client.session_path(credentials.project_id, session_id)
    
    text_input = dialogflow.types.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.types.QueryInput(text=text_input)
    response = session_client.detect_intent(session=session, query_input=query_input)
    
    data = pd.to_datetime("2023-04-01").strftime('%Y-%m-%d')
    year = st.number_input("Ano de escolha", min_value=2024, max_value=2024, value=2024)
    holidays = get_holiday_data(year)
    weather_data = get_weather_data()
    holidays_weather = get_weather_and_holiday_data(holidays, weather_data)
    holidays_weather = add_weather_description(holidays_weather)
    
    #### MAPA DE INTENÇÕES ####
    intent_to_function = {
        'ChamadosAbertosDia': lambda: render_total_chamados_abertos(data),
        'TipoChamadoMaisRegistros': lambda: render_tipo_mais_chamados(data),
        'BairrosMaisChamados': lambda: render_bairros_mais_chamados(data),
        'SubprefeituraMaisChamados': lambda: render_subprefeitura_mais_chamados(data),
        'ChamadosSemBairro': lambda: render_chamados_sem_bairro(data),
        'PerturbacaoSossego': render_perturbacao_sossego,
        'ChamadosDuranteEventos': render_chamados_durante_eventos,
        'ChamadosPorEvento': render_chamados_por_evento,
        'MediaDiariaPorEvento': render_media_diaria_por_evento,
        'ComparacaoMediaDiaria': render_comparacao_media_diaria,
        'TotalFeriados': lambda: render_total_feriados(year),
        'FeriadosPorMes': lambda: render_feriados_por_mes(holidays),
        'FeriadosDiasUteis': lambda: render_feriados_dias_uteis(holidays),
        'TemperaturaMediaPorMes': render_temperatura_media_por_mes,
        'TempoPredominantePorMes': render_tempo_predominante_por_mes,
        'TempoETempMediaFeriados': lambda: render_tempo_e_temp_media_feriados(holidays, weather_data),
        'FeriadosNaoAproveitaveis': lambda: render_feriados_nao_aproveitaveis(holidays_weather),
        'FeriadoMaisAproveitavel': lambda: render_feriado_mais_aproveitavel(holidays_weather),
    }
    ##########################
    
    detected_intent = response.query_result.intent.display_name
    if detected_intent in intent_to_function:
        intent_to_function[detected_intent]()
    return response.query_result.fulfillment_text