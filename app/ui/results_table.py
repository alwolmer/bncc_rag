import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

def render_results_table(resultados):
    if not resultados:
        return pd.DataFrame()  # Retorna vazio, mas evita erro

    df_resultados = pd.DataFrame(resultados)

    if df_resultados.empty:
        return pd.DataFrame()

    df_resultados = pd.DataFrame(resultados)
    st.subheader("Resultados encontrados")

    gb = GridOptionsBuilder.from_dataframe(df_resultados)
    gb.configure_selection(
        selection_mode="multiple",
        use_checkbox=True,
        pre_selected_rows=[],
    )
    gb.configure_column("Habilidade", wrapText=True, autoHeight=True)
    gb.configure_column("Código", headerCheckboxSelection=True)
    gb.configure_grid_options(domLayout='autoHeight')

    grid_options = gb.build()

    grid_response = AgGrid(
        df_resultados,
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,
        fit_columns_on_grid_load=True,
        height=400
    )

    return pd.DataFrame(grid_response["selected_rows"])
