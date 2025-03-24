import streamlit as st
import pandas as pd
import os
from st_files_connection import FilesConnection
from langchain_community.vectorstores import FAISS
from langchain_google_vertexai import VertexAIEmbeddings
from google.oauth2 import service_account
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode


# Set the name of the page
st.set_page_config(
    page_title="Sugestão de Habilidades da BNCC",
    page_icon="📚")

# os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = st.secrets["connections"]["gcs"]

if st.secrets["connections"]["gcs"]:
    creds_dict = st.secrets["connections"]["gcs"]  # or ["google"]
    credentials = service_account.Credentials.from_service_account_info(creds_dict)

@st.cache_resource
def load_vector_store(load_local=st.secrets["settings"]["load_local"]):
    if not load_local:
        conn = st.connection('gcs', type=FilesConnection)

        bucket = st.secrets['project']['bucket']

        # Connect to GCS
        index_path = f'{bucket}/index.faiss'
        meta_path = f'{bucket}/index.pkl'

        # Create temporary local folder
        local_dir = '/tmp/bncc_faiss_index'
        os.makedirs(local_dir, exist_ok=True)

        # Download and save files locally
        with conn.open(index_path, "rb") as f:
            with open(os.path.join(local_dir, "index.faiss"), "wb") as out_f:
                out_f.write(f.read())

        with conn.open(meta_path, "rb") as f:
            with open(os.path.join(local_dir, "index.pkl"), "wb") as out_f:
                out_f.write(f.read())
    else:
        # add data/bncc_faiss_index to the path where current file is
        local_dir = os.path.join(os.path.dirname(__file__), "data")

    embeddings = VertexAIEmbeddings(
        model_name="text-multilingual-embedding-002",
        project=st.secrets["project"]["project_id"],
        location=st.secrets["project"]["region"],
        credentials=credentials
    )

    return FAISS.load_local(local_dir, embeddings, allow_dangerous_deserialization=True)


def search_bncc(vector_score, query, k=5, filtro_componente=None, filtro_ano=None, somente_metadados=False):
    """
    Search FAISS for the most relevant BNCC topics, returning metadata.
    """

    # Build filter dictionary
    filters = {}
    if filtro_componente:
        filters["Componente"] = filtro_componente
    if filtro_ano:
        filters["Ano"] = filtro_ano

    # Run FAISS similarity search with filters
    results = vector_score.similarity_search(query, k=k, filter=filters)

    if not results:
        print("Não foram encontrados resultados")
        return None
    else:
        if somente_metadados:
            return [result.metadata for result in results]
        else:
            return [result.page_content for result in results]

vector_store = load_vector_store()

st.title("Sugestão de Habilidades da BNCC")

# Acessa todos os documentos armazenados
docs = vector_store.docstore._dict.values()

# Extrai valores únicos de 'Ano' e 'Componente'
anos = sorted({doc.metadata.get("Ano") for doc in docs if "Ano" in doc.metadata})
componentes = sorted({doc.metadata.get("Componente") for doc in docs if "Componente" in doc.metadata})

# Inicializa o campo no session_state
if "plano" not in st.session_state:
    st.session_state["plano"] = ""

# Inicializa os resultados da busca
if "resultados" not in st.session_state:
    st.session_state["resultados"] = []

if "filtro_componentes" not in st.session_state:
    st.session_state["filtro_componentes"] = []

if "filtro_anos" not in st.session_state:
    st.session_state["filtro_anos"] = []

# Função para limpar o texto
def limpar_plano():
    st.session_state["plano"] = ""
    st.session_state["resultados"] = []

st.subheader("Filtros")
col1, col2 = st.columns([1, 1])
with col1:
    st.multiselect("Componentes curriculares:", componentes, key="filtro_componentes")
with col2:
    st.multiselect("Anos:", anos, key="filtro_anos")

# Texto do plano controlado por session_state
st.subheader("Plano de aula")
st.text_area("Digite seu plano de aula:", key="plano")

# Botões lado a lado
col3, col4 = st.columns([1, 1])
with col3:
    buscar = st.button("🔍 Buscar habilidades")
with col4:
    st.button("🧹 Limpar texto", on_click=limpar_plano)

# Lógica do botão "Buscar"
if buscar:
    plano = st.session_state["plano"].strip()

    if plano:
        filtros = {}
        if st.session_state["filtro_componentes"]:
            filtros["Componente"] = st.session_state["filtro_componentes"]
        if st.session_state["filtro_anos"]:
            filtros["Ano"] = st.session_state["filtro_anos"]

        st.session_state["resultados"] = search_bncc(
            vector_store,
            plano,
            filtro_ano=filtros.get("Ano"),
            filtro_componente=filtros.get("Componente"),
            somente_metadados=True
        )

        if not st.session_state["resultados"]:
            st.warning("Nenhum resultado encontrado com os filtros selecionados.")
    else:
        st.warning("Digite um plano de aula antes de buscar.")

resultados = st.session_state["resultados"]

if resultados:
    df_resultados = pd.DataFrame(resultados)

    st.subheader("Resultados encontrados")

    gb = GridOptionsBuilder.from_dataframe(df_resultados)
    gb.configure_selection(
        selection_mode="multiple",
        use_checkbox=True,
        pre_selected_rows=[],
    )
    gb.configure_column("Habilidade", wrapText=True, autoHeight=True)
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

    selecionados_df = pd.DataFrame(grid_response["selected_rows"])

    if not selecionados_df.empty:
        codigos = ", ".join(selecionados_df["Código"])
        habilidades = "; ".join(f"{row['Código']} - {row['Habilidade']}" for _, row in selecionados_df.iterrows())

        st.markdown("### Copiar seleção")
        col1, col2 = st.columns(2)
        with col1:
            st.code(codigos, language="text", wrap_lines=True)
        with col2:
            st.code(habilidades, language="text", wrap_lines=True)
    else:
        st.info("Selecione ao menos uma linha da tabela para copiar os códigos.")