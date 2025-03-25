import streamlit as st
from utils.logger import log_event
import json

def render_copy_actions(selecionados_df):
    codigos = ", ".join(selecionados_df["Código"])
    habilidades = "; ".join(f"{row['Código']} - {row['Habilidade']}" for _, row in selecionados_df.iterrows())

    if st.button("✅ Confirmar seleção"):
        st.success(f"{len(selecionados_df)} habilidade(s) selecionada(s).")

        log_event("sucesso")
        
        st.markdown("### Copiar seleção")
        col1, col2 = st.columns(2)
        with col1:
            st.code(codigos, language="text", wrap_lines=True)
        with col2:
            st.code(habilidades, language="text", wrap_lines=True)
    else:
        st.info("Confirme a seleção para copiar códigos e habilidades.")

def set_feedback_enviado():
    st.session_state["feedback_enviado"] = True

def set_irrelevant_feedback():
    log_event("resultado_irrelevante")
    set_feedback_enviado()

def set_no_result_feedback():
    log_event("sem_resultado")
    set_feedback_enviado()

def render_feedback_thanks():
    st.info("Obrigado pelo feedback. Pedimos desculpas pelo transtorno e usaremos essa indicação para melhorar nossas predições.")

def render_no_result_feedback():
    st.info("É importante para nós saber se você não encontrou o que procurava. Se tem certeza da sua busca e não encontrou resultados, clique no botão abaixo.")
    st.button("🚫 Nenhuma habilidade encontrada", on_click=set_no_result_feedback)
   
def render_bad_result_feedback():
    st.info("É importante para nós saber se você não encontrou o que procurava. Se tem certeza da sua busca e não encontrou resultados relevantes, clique no botão abaixo.")
    st.button("🚫 Nenhuma habilidade relevante", on_click=set_irrelevant_feedback)