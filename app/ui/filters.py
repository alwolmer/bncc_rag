import streamlit as st
from utils.session_state import update_search_filters

def render_filtros():
    fund_em = st.radio("Nível de ensino:", ["Fundamental", "Médio"])
    if fund_em == "Fundamental":
        docs = st.session_state["vector_store_fund"].docstore._dict.values()
    else:
        docs = st.session_state["vector_store_em"].docstore._dict.values()

    anos = sorted({doc.metadata.get("Ano") for doc in docs if "Ano" in doc.metadata})
    componentes = sorted({doc.metadata.get("Componente") for doc in docs if "Componente" in doc.metadata})

    col1, col2 = st.columns([1, 1])
    with col1:
        filtro_componentes = st.multiselect("Componentes curriculares:", componentes)
    with col2:
        filtro_anos = st.multiselect("Anos:", anos)
    
    if st.session_state["update_busca"]:
        update_search_filters(
            componentes=filtro_componentes,
            anos=filtro_anos,
            ensino_medio=fund_em == "Médio"
        )