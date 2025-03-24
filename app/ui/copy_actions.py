import streamlit as st

def render_copy_actions(selecionados_df):
    codigos = ", ".join(selecionados_df["Código"])
    habilidades = "; ".join(f"{row['Código']} - {row['Habilidade']}" for _, row in selecionados_df.iterrows())

    if st.button("✅ Confirmar seleção"):
        st.success(f"{len(selecionados_df)} habilidade(s) selecionada(s).")

        st.markdown("### Copiar seleção")
        col1, col2 = st.columns(2)
        with col1:
            st.code(codigos, language="text", wrap_lines=True)
        with col2:
            st.code(habilidades, language="text", wrap_lines=True)
    else:
        st.info("Confirme a seleção para copiar códigos e habilidades.")


def render_feedback_button():
    if st.button("🚫 Nenhuma habilidade corresponde"):
        st.info("Sinalizado: nenhuma habilidade sugerida era adequada. Pedimos desculpas pelo transtorno e usaremos essa indicação para melhorar nossas predições.")