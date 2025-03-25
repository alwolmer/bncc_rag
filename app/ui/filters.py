import streamlit as st

def render_filtros(anos, componentes):
    col1, col2 = st.columns([1, 1])
    with col1:
        filtro_componentes = st.multiselect("Componentes curriculares:", componentes)
    with col2:
        filtro_anos = st.multiselect("Anos:", anos)
    
    if st.session_state["update_busca"]:
        st.session_state["filtros"]["componentes"] = filtro_componentes
        st.session_state["filtros"]["anos"] = filtro_anos