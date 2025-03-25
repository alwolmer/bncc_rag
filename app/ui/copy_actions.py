import streamlit as st
from utils.logger import log_event
import json

def render_copy_actions(selecionados_df):
    codigos = ", ".join(selecionados_df["Código"])
    habilidades = "; ".join(f"{row['Código']} - {row['Habilidade']}" for _, row in selecionados_df.iterrows())

    if st.button("✅ Confirmar seleção"):
        st.success(f"{len(selecionados_df)} habilidade(s) selecionada(s).")

        log_event(
            evento="sucesso",
            plano=st.session_state["plano"],
            filtros=st.session_state["filtros"],
            resultados=st.session_state["codigos_resultados"]
        )
        
        st.markdown("### Copiar seleção")
        col1, col2 = st.columns(2)
        with col1:
            st.code(codigos, language="text", wrap_lines=True)
        with col2:
            st.code(habilidades, language="text", wrap_lines=True)
    else:
        st.info("Confirme a seleção para copiar códigos e habilidades.")

def render_feedback_button(result: bool):
    st.info("É importante para nós saber se você não encontrou o que procurava. Se tem certeza da sua busca e não encontrou resultados relevantes, clique no botão abaixo.")
    if st.button("🚫 Nenhuma habilidade corresponde"):
        if result:
            log_event(
                evento="resultado_inadequado",
                plano=st.session_state["plano"],
                filtros=st.session_state["filtros"],
                resultados=st.session_state["codigos_resultados"]
            )
            st.info("Sinalizado: nenhuma habilidade entre as sugeridas era relevante. Pedimos desculpas pelo transtorno e usaremos essa indicação para melhorar nossas predições.")
        else:
            log_event(
                evento="sem_resultado",
                plano=st.session_state["plano"],
                filtros=st.session_state["filtros"],
                resultados=st.session_state["codigos_resultados"]
            )
            st.info("Sinalizado: a busca não retornou resultados. Pedimos desculpas pelo transtorno e usaremos essa indicação para melhorar nossas predições.")