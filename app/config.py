import streamlit as st
from google.oauth2 import service_account

# Carrega configurações gerais do projeto
PROJECT_ID = st.secrets["project"]["project_id"]
REGION = st.secrets["project"]["region"]
FUND_BUCKET = st.secrets["project"]["fund_bucket"]
EM_BUCKET = st.secrets["project"]["em_bucket"]
LOAD_LOCAL = st.secrets["settings"].get("load_local", False)
LOGS_TABLE = st.secrets["settings"]["logs_table"]

# Carrega credenciais do GCS/Vertex
if st.secrets["connections"]["gcs"]:
    CREDS_DICT = st.secrets["connections"]["gcs"]
    CREDENTIALS = service_account.Credentials.from_service_account_info(CREDS_DICT)
else:
    CREDENTIALS = None