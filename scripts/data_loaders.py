from google.cloud import bigquery
from google.oauth2 import service_account
from dotenv import load_dotenv
import os

load_dotenv()

def run_query(query):
    credentials = service_account.Credentials.from_service_account_info({
        "type": os.getenv('TYPE'),
        "project_id": os.getenv('PROJECT_ID'),
        "private_key_id": os.getenv('PRIVATE_KEY_ID'),
        "private_key": os.getenv('PRIVATE_KEY').replace('\\n', '\n'),
        "client_email": os.getenv('CLIENT_EMAIL'),
        "client_id": os.getenv('CLIENT_ID'),
        "auth_uri": os.getenv('AUTH_URI'),
        "token_uri": os.getenv('TOKEN_URI'),
        "auth_provider_x509_cert_url": os.getenv('AUTH_PROVIDER_X509_CERT_URL'),
        "client_x509_cert_url": os.getenv('CLIENT_X509_CERT_URL'),
        "universe_domain": os.getenv('UNIVERSE_DOMAIN')
    })

    client = bigquery.Client(credentials=credentials, project=os.getenv('PROJECT_ID'))

    df = client.query(query).to_dataframe(geography_as_object=True, progress_bar_type='tqdm')

    return df
