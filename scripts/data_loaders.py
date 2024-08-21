from google.cloud import bigquery
from google.oauth2 import service_account
from dotenv import load_dotenv
import os

load_dotenv()

def run_query(query):
    credentials = service_account.Credentials.from_service_account_file(os.getenv('CREDENTIALS_PATH'))
    client = bigquery.Client(credentials=credentials, project="datascientist-fz")
    
    
    df = client.query(query).to_dataframe(geography_as_object=True,progress_bar_type='tqdm')
    
    return df