import streamlit as st

def render_input_box():
    st.subheader("Plano de aula")
    st.text_area("Digite seu plano de aula:", key="plano")

    col1, col2 = st.columns([1, 1])
    with col1:
        buscar = st.button("🔍 Buscar habilidades")
    with col2:
        limpar = st.button("🧹 Limpar texto")

    return buscar, limpar