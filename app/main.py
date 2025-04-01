import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import streamlit as st

st.set_page_config(page_title="Sugestão de Habilidades da BNCC", page_icon="📚")

import pandas as pd
from vectorstore.loader import load_embeddings, load_vector_store, load_retriever
from vectorstore.search import search_bncc
from utils.session_state import init_all_state, clear_search, update_search_filters
from ui.filters import render_filtros
from ui.input_box import render_input_box
from ui.results_table import render_results_table
from ui.copy_actions import render_copy_actions, render_no_result_feedback, render_feedback_thanks, render_bad_result_feedback
from utils.logger import init_connection, log_access
from chain.graph import create_chain_graph, run_chain



# Initialize all session state
init_all_state()

# Initialize application resources
st.session_state["db_conn"] = init_connection()
st.session_state["embeddings"] = load_embeddings()
st.session_state["vector_store_fund"] = load_vector_store('fund')
st.session_state["vector_store_em"] = load_vector_store('em')
st.session_state["ai_chain_fund"] = create_chain_graph(load_retriever('fund'))
st.session_state["ai_chain_em"] = create_chain_graph(load_retriever('em'))

# Log access if not already logged
if not st.session_state["access_logged"]:
    log_access()

# Render UI components
st.title("Sugestão de Habilidades da BNCC")
render_filtros()
render_input_box()

# Handle AI treatment
if st.session_state.get("tratar_com_ia", False):
    plano = st.session_state["plano"].strip()
    if plano:
        # Validate filters
        anos = st.session_state["filtros"].get("anos", [])
        componentes = st.session_state["filtros"].get("componentes", [])
        
        if not st.session_state["ensino_medio"] and (not anos or len(anos) > 1):
            st.error("Por favor, selecione um e apenas um ano para a análise com IA.")
            st.session_state["tratar_com_ia"] = False
        elif not componentes or len(componentes) > 2:
            st.error("Por favor, selecione ao menos um eno máximo dois componentes curriculares para a análise com IA.")
            st.session_state["tratar_com_ia"] = False
        else:
            with st.spinner("Analisando plano com IA..."):
                etapa = "Ensino Médio" if st.session_state["ensino_medio"] else "Ensino Fundamental"
                ano = anos[0] if anos else ""
                componentes = componentes if componentes else []
                
                # Update search parameters
                st.session_state.update({
                    "update_busca": False,
                    "feedback_enviado": False
                })

                ai_chain = st.session_state["ai_chain_em"] if st.session_state["ensino_medio"] else st.session_state["ai_chain_fund"]

                # result = ai_chain.invoke({
                #     "plano": plano,
                #     "etapa": etapa,
                #     "ano": ano,
                #     "componentes": componentes
                # })
                
                result = run_chain(
                    st.session_state["ai_chain_em"] if st.session_state["ensino_medio"] else st.session_state["ai_chain_fund"],
                    plano=plano,
                    etapa=etapa,
                    ano=ano,
                    componentes=componentes
                )
                
                if result["status"] == "success":
                    if result["plano_ok"] and result["habilidades_ok"]:

                        avaliacao_estrutura = result["avaliacao_estrutura"]
                        
                        st.session_state["resultados"] = [
                            {"Código": codigo, "Habilidade": hab} 
                            for codigo, hab in zip(result["codigos_bncc"], result["habilidades_bncc"])
                        ]
                        st.session_state["codigos_resultados"] = result["codigos_bncc"]
                        st.success("Plano analisado com sucesso!")
                        
                        # Display avaliação results
                        st.markdown("# Avaliação do Plano")

                        st.markdown("## **Habilidades selecionadas**")
                        st.code(
                            "\n".join(avaliacao_estrutura["habilidades_bncc"]),
                            language="text",
                            wrap_lines=True
                        )

                        
                        # Helper function to render subtopic
                        def render_subtopic(title: str, data: dict):
                            st.markdown(f"## **{title}**")
                            if data["presente"]:
                                st.code(
                                    data["identificacao"], 
                                    language="text",
                                    wrap_lines=True
                                )
                            elif not data["adequado"]:
                                st.error("❌ Não identificado no plano")
                            else:
                                st.success("✅ Não identificado no plano, mas adequado")

                            if not data["adequado"] and data["sugestao_melhoria"]:
                                    st.markdown(f"**Sugestão de melhoria**")
                                    st.code(
                                        data["sugestao_melhoria"],
                                        language="text",
                                        wrap_lines=True
                                    )
                        
                        # Render each subtopic
                        render_subtopic("Objetivos", avaliacao_estrutura["objetivos"])
                        render_subtopic("Conteúdos", avaliacao_estrutura["conteudos"])
                        render_subtopic("Metodologia", avaliacao_estrutura["metodologia"])
                        render_subtopic("Avaliação", avaliacao_estrutura["avaliacao"])
                        render_subtopic("Recursos", avaliacao_estrutura["recursos"])
                        render_subtopic("Materiais", avaliacao_estrutura["materiais"])
                        render_subtopic("Tempo", avaliacao_estrutura["tempo"])
                    else:
                        if not result["plano_ok"]:
                            st.error("Acreditamos que o texto submetido não é um plano de aula válido.")
                        if not result["habilidades_ok"]:
                            st.error("Não localizamos habilidades da BNCC relevantes para o plano de aula.")
                else:
                    st.error(f"Erro ao analisar o plano: {result['error']}")
    else:
        st.warning("Digite um plano de aula antes de usar a análise com IA.")
    
    st.session_state["tratar_com_ia"] = False

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