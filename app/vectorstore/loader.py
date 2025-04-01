import os
from langchain_community.vectorstores import FAISS
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_core.vectorstores import VectorStoreRetriever
from st_files_connection import FilesConnection
from langchain_google_vertexai import ChatVertexAI
import streamlit as st
from config import LOAD_LOCAL, FUND_BUCKET, EM_BUCKET, PROJECT_ID, REGION, CREDENTIALS

class FilterableRetriever(VectorStoreRetriever):
    def invoke_with_filters(self, query: str, **kwargs):
        return self.vectorstore.similarity_search(query, **kwargs)

@st.cache_resource
def load_embeddings():
    return VertexAIEmbeddings(
        model_name="text-multilingual-embedding-002",
        project=PROJECT_ID,
        location=REGION,
        credentials=CREDENTIALS
    )

@st.cache_resource
def load_vector_store(store="fund"):
    if not LOAD_LOCAL:
        conn = st.connection('gcs', type=FilesConnection)

        if store == "fund":
            index_path = f'{FUND_BUCKET}/index.faiss'
            meta_path = f'{FUND_BUCKET}/index.pkl'
            local_dir = '/tmp/bncc_faiss_index'
        else:
            index_path = f'{EM_BUCKET}/index.faiss'
            meta_path = f'{EM_BUCKET}/index.pkl'
            local_dir = '/tmp/bncc_faiss_index_em'
        
        os.makedirs(local_dir, exist_ok=True)

        with conn.open(index_path, "rb") as f:
            with open(os.path.join(local_dir, "index.faiss"), "wb") as out_f:
                out_f.write(f.read())

        with conn.open(meta_path, "rb") as f:
            with open(os.path.join(local_dir, "index.pkl"), "wb") as out_f:
                out_f.write(f.read())
    else:
        if store == "fund":
            local_dir = os.path.join(os.path.dirname(__file__), "../../data/fund")
        else:
            local_dir = os.path.join(os.path.dirname(__file__), "../../data/em")
    

    return FAISS.load_local(local_dir, st.session_state['embeddings'], allow_dangerous_deserialization=True)

@st.cache_resource
def load_retriever(store: str ="fund"):
    vectorstore = load_vector_store(store)
    retriever = FilterableRetriever(
        vectorstore=vectorstore,
        search_kwargs={"k": 6}
    )
    return retriever

@st.cache_resource
def load_llm():
    return ChatVertexAI(
        model_name="gemini-2.0-flash-lite",
        temperature=0,
        project=PROJECT_ID,
        location=REGION,
        credentials=CREDENTIALS
    )