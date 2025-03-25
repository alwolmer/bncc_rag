import streamlit as st

def search_bncc(query, k=5, filtro_componente=None, filtro_ano=None, somente_metadados=False, em=False):
    filters = {}
    if filtro_componente:
        filters["Componente"] = filtro_componente
    if not em:
        if filtro_ano:
            filters["Ano"] = filtro_ano
        results = st.session_state['vector_store_fund'].similarity_search(query, k=k, filter=filters)
    else:
        results = st.session_state['vector_store_em'].similarity_search(query, k=k, filter=filters)

    if not results:
        return None
    return [result.metadata if somente_metadados else result.page_content for result in results]