import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
from vectorstore.loader import load_embeddings, load_vector_store
from vectorstore.search import search_bncc
from utils.session_state import init_all_state, clear_search, update_search_filters
from ui.filters import render_filtros
from ui.input_box import render_input_box
from ui.results_table import render_results_table
from ui.copy_actions import render_copy_actions, render_no_result_feedback, render_feedback_thanks, render_bad_result_feedback
from utils.logger import init_connection, log_access

st.set_page_config(page_title="Sugestão de Habilidades da BNCC", page_icon="📚")

# Initialize all session state
init_all_state()

# Initialize application resources
st.session_state["db_conn"] = init_connection()
st.session_state["embeddings"] = load_embeddings()
st.session_state["vector_store_fund"] = load_vector_store('fund')
st.session_state["vector_store_em"] = load_vector_store('em')

# Log access if not already logged
if not st.session_state["access_logged"]:
    log_access()

# Render UI components
st.title("Sugestão de Habilidades da BNCC")
render_filtros()
render_input_box()

# Handle search
plano = st.session_state["plano"].strip()
if plano and st.session_state["update_busca"]:
    st.session_state.update({"update_busca": False, "feedback_enviado": False})
    st.session_state["resultados"] = search_bncc(
        plano,
        filtro_componente=st.session_state["filtros"].get("componentes"),
        filtro_ano=st.session_state["filtros"].get("anos"),
        somente_metadados=True,
        em=st.session_state["ensino_medio"]
    )

    if st.session_state["resultados"]:
        st.session_state["codigos_resultados"] = [resultado["Código"] for resultado in st.session_state["resultados"]]
    else:
        st.warning("Nenhum resultado encontrado com os filtros selecionados.")
        render_no_result_feedback()

elif not plano:
    st.warning("Digite um plano de aula antes de buscar.")

# Handle results display
if st.session_state["resultados"]:
    st.session_state["selecionados_df"] = render_results_table(st.session_state["resultados"])
    if not st.session_state["selecionados_df"].empty and not st.session_state["feedback_enviado"]:
        st.session_state["selecionados"] = st.session_state["selecionados_df"]["Código"].tolist()
        render_copy_actions(st.session_state["selecionados_df"])
    elif not st.session_state["feedback_enviado"]:
        render_bad_result_feedback()

if st.session_state["feedback_enviado"]:
    render_feedback_thanks()