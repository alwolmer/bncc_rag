import streamlit as st
import json
from supabase import create_client, Client
from config import LOGS_TABLE

@st.cache_resource
def init_connection():
    url = st.secrets["db"]["SUPABASE_URL"]
    key = st.secrets["db"]["SUPABASE_KEY"]
    return create_client(url, key)


def stringify(obj):
    return ', '.join([str(i) for i in obj])

def log_event(evento: str):
    try:
        conn = st.session_state["db_conn"]

        response = conn.table(LOGS_TABLE).insert({
            "evento": evento,
            "plano": st.session_state["plano"],
            "nivel": "fundamental" if not st.session_state["ensino_medio"] else "médio",
            "filtro_ano": stringify(st.session_state['filtros']['anos']) if st.session_state['filtros']['anos'] else None,
            "filtro_componente": stringify(st.session_state['filtros']['componentes']) if st.session_state['filtros']['componentes'] else None,
            "resultados": stringify(st.session_state["codigos_resultados"]) if st.session_state["codigos_resultados"] else None,
            "selecionados": stringify(st.session_state["selecionados"]) if st.session_state["selecionados"] else None

        }).execute()

        # print("✅ Log registrado com sucesso.")
    except Exception as e:
        print("Erro com log")
        print("Erro ao inserir log:", e)