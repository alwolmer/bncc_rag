import streamlit as st
from supabase import create_client
from config import LOGS_TABLE, ACCESS_TABLE

import threading
import requests
from user_agents import parse as parse_ua
from streamlit_js_eval import streamlit_js_eval

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

def classify_device(ua):
    is_mobile = ua.is_mobile
    is_tablet = ua.is_tablet
    is_pc = ua.is_pc

    categories = {
        "Mobile": is_mobile,
        "Tablet": is_tablet,
        "Desktop": is_pc,
    }
    true_categories = [k for k, v in categories.items() if v]

    return true_categories[0] if len(true_categories) == 1 else "Unknown"


def async_log_user_info(user_agent):
    try:

        # Parse user agent
        ua = parse_ua(user_agent)
        device_type = classify_device(ua)

        # Try to get IP
        try:
            ip = requests.get("https://api64.ipify.org?format=json", timeout=2).json().get("ip")
        except:
            ip = None

        log_data = {
            "ip": ip,
            "browser": f"{ua.browser.family}",
            "browser_version": f"{ua.browser.version_string}",
            "os": f"{ua.os.family}",
            "os_version": f"{ua.os.version_string}",
            "device": device_type,
        }

        # print("Log de acesso:", log_data)

        conn = init_connection()

        conn.table(ACCESS_TABLE).insert(log_data).execute()
        # print("✅ Access log sent.")

    except Exception as e:
        print("Erro ao processar ou enviar log de acesso:", e)


def log_access():
    user_agent = streamlit_js_eval(js_expressions="window.navigator.userAgent", key="ua")

    if user_agent:
        # Dispara thread com coleta e envio
        thread = threading.Thread(target=async_log_user_info, args=(user_agent,))
        thread.start()

        st.session_state["access_logged"] = True