import streamlit as st
from vectorstore.loader import load_vector_store
from vectorstore.search import search_bncc
from utils.session import init_session_state
from ui.filters import render_filtros
from ui.input_box import render_input_box
from ui.results_table import render_results_table
from ui.copy_actions import render_copy_actions, render_feedback_button

from utils.logger import init_connection

st.set_page_config(page_title="Sugestão de Habilidades da BNCC", page_icon="📚")

# Inicializa o FAISS
init_session_state("vector_store", load_vector_store())

# Inicializa conexão com o banco de dados para log
init_session_state("db_conn", init_connection())

# Inicializa estado
init_session_state("plano", "")
init_session_state("resultados", [])
init_session_state("codigos_resultados", [])

init_session_state("filtros", {})

init_session_state("update_busca", False)

init_session_state("buscar", False)

# Carrega documentos e extrai filtros
docs = st.session_state["vector_store"].docstore._dict.values()
anos = sorted({doc.metadata.get("Ano") for doc in docs if "Ano" in doc.metadata})
componentes = sorted({doc.metadata.get("Componente") for doc in docs if "Componente" in doc.metadata})

# Renderiza filtros e entrada do plano
st.title("Sugestão de Habilidades da BNCC")
render_filtros(anos, componentes)
buscar, limpar = render_input_box()

# Busca habilidades
# if st.session_state["update_busca"]:
plano = st.session_state["plano"].strip()
if plano:
    st.session_state["resultados"] = search_bncc(
        st.session_state["vector_store"],
        plano,
        filtro_componente=st.session_state["filtros"].get("componentes"),
        filtro_ano=st.session_state["filtros"].get("anos"),
        somente_metadados=True
    )

    if st.session_state["resultados"]:
        st.session_state["codigos_resultados"] = [resultado["Código"] for resultado in st.session_state["resultados"]]

    if not st.session_state["resultados"]:
        st.warning("Nenhum resultado encontrado com os filtros selecionados.")
        render_feedback_button(False)
else:
    st.warning("Digite um plano de aula antes de buscar.")

# Resultados
resultados = st.session_state["resultados"]
if resultados:
    selecionados_df = render_results_table(resultados)
    if not selecionados_df.empty:
        render_copy_actions(selecionados_df)
    else:
        render_feedback_button(True)
