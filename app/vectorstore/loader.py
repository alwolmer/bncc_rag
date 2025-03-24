import os
from langchain_community.vectorstores import FAISS
from langchain_google_vertexai import VertexAIEmbeddings
from st_files_connection import FilesConnection
import streamlit as st
from config import LOAD_LOCAL, BUCKET, PROJECT_ID, REGION, CREDENTIALS

@st.cache_resource
def load_vector_store():
    if not LOAD_LOCAL:
        conn = st.connection('gcs', type=FilesConnection)

        index_path = f'{BUCKET}/index.faiss'
        meta_path = f'{BUCKET}/index.pkl'

        local_dir = '/tmp/bncc_faiss_index'
        os.makedirs(local_dir, exist_ok=True)

        with conn.open(index_path, "rb") as f:
            with open(os.path.join(local_dir, "index.faiss"), "wb") as out_f:
                out_f.write(f.read())

        with conn.open(meta_path, "rb") as f:
            with open(os.path.join(local_dir, "index.pkl"), "wb") as out_f:
                out_f.write(f.read())
    else:
        local_dir = os.path.join(os.path.dirname(__file__), "../../data")

    embeddings = VertexAIEmbeddings(
        model_name="text-multilingual-embedding-002",
        project=PROJECT_ID,
        location=REGION,
        credentials=CREDENTIALS
    )

    return FAISS.load_local(local_dir, embeddings, allow_dangerous_deserialization=True)