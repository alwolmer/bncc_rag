import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
from vectorstore.loader import load_embeddings, load_vector_store
from vectorstore.search import search_bncc
from utils.session import init_session_state
from ui.filters import render_filtros
from ui.input_box import render_input_box
from ui.results_table import render_results_table
from ui.copy_actions import render_copy_actions, render_no_result_feedback, render_feedback_thanks, render_bad_result_feedback

from utils.logger import init_connection

st.set_page_config(page_title="Sugestão de Habilidades da BNCC", page_icon="📚")

# Inicializa o FAISS
init_session_state("embeddings", load_embeddings())
init_session_state("vector_store_fund", load_vector_store('fund'))
init_session_state("vector_store_em", load_vector_store('em'))

# Inicializa conexão com o banco de dados para log
init_session_state("db_conn", init_connection())

# Inicializa estado
init_session_state("plano", "")
init_session_state("resultados", [])
init_session_state("codigos_resultados", [])

init_session_state("ensino_medio", False)
init_session_state("filtros", {})

init_session_state("update_busca", False)
init_session_state("feedback_enviado", False)

init_session_state("selecionados", [])

init_session_state("selecionados_df", pd.DataFrame())

# Renderiza filtros e entrada do plano
st.title("Sugestão de Habilidades da BNCC")
render_filtros()
render_input_box()

# Busca habilidades
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

if st.session_state["resultados"]:
    st.session_state["selecionados_df"] = render_results_table(st.session_state["resultados"])
    if not st.session_state["selecionados_df"].empty and not st.session_state["feedback_enviado"]:
        st.session_state["selecionados"] = st.session_state["selecionados_df"]["Código"].tolist()
        render_copy_actions(st.session_state["selecionados_df"])
    elif not st.session_state["feedback_enviado"]:
        render_bad_result_feedback()
# elif not st.session_state["feedback_enviado"]:
#     render_no_result_feedback()

if st.session_state["feedback_enviado"]:
    render_feedback_thanks()

# if (not st.session_state["selecionados"]) or st.session_state["feedback_enviado"]:
#     render_feedback_button()
# else:
#     render_copy_actions(st.session_state["selecionados_df"])