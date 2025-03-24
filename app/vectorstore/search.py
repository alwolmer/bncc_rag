def search_bncc(vector_store, query, k=5, filtro_componente=None, filtro_ano=None, somente_metadados=False):
    filters = {}
    if filtro_componente:
        filters["Componente"] = filtro_componente
    if filtro_ano:
        filters["Ano"] = filtro_ano

    results = vector_store.similarity_search(query, k=k, filter=filters)

    if not results:
        return None
    return [result.metadata if somente_metadados else result.page_content for result in results]