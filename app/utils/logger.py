import streamlit as st
import json
from supabase import create_client, Client

@st.cache_resource
def init_connection():
    url = st.secrets["db"]["SUPABASE_URL"]
    key = st.secrets["db"]["SUPABASE_KEY"]
    return create_client(url, key)


def log_event(evento, plano, filtros=None, resultados=None):
    try:
        conn = st.session_state["db_conn"]

        conn.table("logs").insert({
            "evento": evento,
            "plano": plano,
            "filtros": filtros if filtros else None,
            "resultados": resultados if resultados else None
        }).execute()

        print("✅ Log registrado com sucesso.")
    except Exception as e:
        print(" Erro ao inserir log:", e)