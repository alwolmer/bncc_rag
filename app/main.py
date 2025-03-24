import streamlit as st
from vectorstore.loader import load_vector_store
from vectorstore.search import search_bncc
from utils.session import init_session_state
from ui.filters import render_filtros
from ui.input_box import render_input_box
from ui.results_table import render_results_table
from ui.copy_actions import render_copy_actions, render_feedback_button

st.set_page_config(page_title="Sugestão de Habilidades da BNCC", page_icon="📚")

# Inicializa o FAISS
vector_store = load_vector_store()

# Inicializa estado
init_session_state("plano", "")
init_session_state("resultados", [])

# Carrega documentos e extrai filtros
docs = vector_store.docstore._dict.values()
anos = sorted({doc.metadata.get("Ano") for doc in docs if "Ano" in doc.metadata})
componentes = sorted({doc.metadata.get("Componente") for doc in docs if "Componente" in doc.metadata})

# Renderiza filtros e entrada do plano
st.title("Sugestão de Habilidades da BNCC")
filtro_componentes, filtro_anos = render_filtros(anos, componentes)
buscar, limpar = render_input_box()

# Limpa plano
if limpar:
    st.session_state["plano"] = ""
    st.session_state["resultados"] = []

# Busca habilidades
if buscar:
    plano = st.session_state["plano"].strip()
    if plano:
        filtros = {}
        if filtro_componentes:
            filtros["Componente"] = filtro_componentes
        if filtro_anos:
            filtros["Ano"] = filtro_anos

        st.session_state["resultados"] = search_bncc(
            vector_store,
            plano,
            filtro_componente=filtros.get("Componente"),
            filtro_ano=filtros.get("Ano"),
            somente_metadados=True
        )

        if not st.session_state["resultados"]:
            st.warning("Nenhum resultado encontrado com os filtros selecionados.")
    else:
        st.warning("Digite um plano de aula antes de buscar.")

# Resultados
resultados = st.session_state["resultados"]
if resultados:
    selecionados_df = render_results_table(resultados)
    if not selecionados_df.empty:
        render_copy_actions(selecionados_df)
    else:
        render_feedback_button()
