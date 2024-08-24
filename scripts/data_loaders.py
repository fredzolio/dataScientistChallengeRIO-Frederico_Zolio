import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

def run_query(query):
    credentials = service_account.Credentials.from_service_account_info({
        "type": st.secrets["google_cloud"]["type"],
        "project_id": st.secrets["google_cloud"]["project_id"],
        "private_key_id": st.secrets["google_cloud"]["private_key_id"],
        "private_key": st.secrets["google_cloud"]["private_key"],
        "client_email": st.secrets["google_cloud"]["client_email"],
        "client_id": st.secrets["google_cloud"]["client_id"],
        "auth_uri": st.secrets["google_cloud"]["auth_uri"],
        "token_uri": st.secrets["google_cloud"]["token_uri"],
        "auth_provider_x509_cert_url": st.secrets["google_cloud"]["auth_provider_x509_cert_url"],
        "client_x509_cert_url": st.secrets["google_cloud"]["client_x509_cert_url"],
        "universe_domain": st.secrets["google_cloud"]["universe_domain"]
    })

    client = bigquery.Client(credentials=credentials, project=st.secrets["google_cloud"]["project_id"])

    df = client.query(query).to_dataframe(geography_as_object=True, progress_bar_type='tqdm')

    return df
