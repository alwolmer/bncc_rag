# input_box.py

import streamlit as st
from utils.session_state import clear_search

def render_input_box():
    # Verifica se é para limpar
    if st.session_state["limpar"]:
        clear_search()
        st.session_state["limpar"] = False
        st.rerun()  # força nova renderização segura

    # Renderiza campo de texto
    st.subheader("Plano de aula")
    st.text_area("Digite seu plano de aula:", key="plano")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.button("🔍 Buscar habilidades", on_click=lambda: st.session_state.update({"update_busca": True}))
    with col2:
        st.button("🧹 Limpar texto", on_click=lambda: st.session_state.update({"limpar": True}))