# input_box.py

import streamlit as st
from utils.session import init_session_state

def render_input_box():
    # Inicializa session_state com segurança
    init_session_state("limpar", False)

    # Verifica se é para limpar
    if st.session_state["limpar"]:
        st.session_state["plano"] = ""
        st.session_state["resultados"] = []
        st.session_state["limpar"] = False
        st.rerun()  # força nova renderização segura

    # Renderiza campo de texto
    st.subheader("Plano de aula")
    st.text_area("Digite seu plano de aula:", key="plano")

    col1, col2 = st.columns([1, 1])
    with col1:
        buscar = st.button("🔍 Buscar habilidades", on_click=lambda: st.session_state.update({"update_busca": True}))
    with col2:
        limpar = st.button("🧹 Limpar texto", on_click=lambda: st.session_state.update({"limpar": True}))

    return buscar, limpar
