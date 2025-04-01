from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnableMap, RunnablePassthrough
from langchain_core.runnables import RunnableBranch
from langchain_core.runnables import chain
from langchain_core.messages import HumanMessage
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from config import CREDENTIALS, PROJECT_ID, REGION

import streamlit as st

from vectorstore.loader import load_llm

llm = load_llm()

# ---- STRUCTURED OUTPUT MODEL FOR EXTRACTION ----
class FirstCheck(BaseModel):
    plano_ok: bool = Field(..., description="Se o texto do plano realmente é um plano de aula, como especificado acima.")
    habilidades_ok: bool = Field(..., description="Se há ao menos uma habilidade da BNCC relevante para o plano, ano e componente.")


fc_parser = PydanticOutputParser(pydantic_object=FirstCheck)

# ---- PROMPT TEMPLATE ----
first_check_prompt = ChatPromptTemplate.from_messages([
    ("system", "Você é um especialista em currículos da educação básica brasileira. Você analisa planos de aula para avaliar se eles atendem a determinados requisitos. Você jamais dá respostas para além dos formatos explicitamente definidos em cada instrução."),
    ("human", '''Plano de aula:
{plano}

Etapa de ensino: {etapa}
Ano: {ano}
Componente(s) curricular(es): {componentes}

Habilidades da BNCC identificadas:
{habilidades_bncc}

Com base nas informações acima, determine:
- Se o texto do plano contém ao menos uma proposta de atividade, dinâmica, conteúdo ou objetivo de aprendizado minimamente condizente com o contexto escolar, etapa de ensino e ano, mesmo que a descrição seja deficiente ou vaga. Preste particular atenção ao fato de que pode haver conteúdo ou proposta de atividade que não esteja explicitamente descrito, mas que pode ser inferido a partir do texto. Não considere como plano de aula textos que não tenham relação com o contexto escolar ou que sejam apenas uma descrição de um conteúdo ou atividade sem relação com o ensino.
- Se ao menos uma das habilidades da BNCC entre as elencadas tem relação com a proposta do plano e é condizente com a etapa, ano e componentes curriculares providos, mesmo que parcialmente. Se não tiverem sido providas quaisquer habilidades, considere que esse requisito não foi atendido.

Retorne apenas no seguinte formato JSON:

{format_instructions}''')
])

# ---- CHAIN ----
first_check_chain = (
    {
        "plano": lambda x: x["plano"],
        "etapa": lambda x: x["etapa"],
        "ano": lambda x: x["ano"],
        "componentes": lambda x: x["componentes"],
        "habilidades_bncc": lambda x: x["habilidades_bncc"],
        "format_instructions": lambda _: fc_parser.get_format_instructions()
    }
    | first_check_prompt
    | llm
    | fc_parser
)

def check_first_check_output(result: FirstCheck, original_input: dict) -> dict:
    return {
        **original_input,
        **result.model_dump()
    }

  # ---- VECTOR STORE RETRIEVAL WRAPPER (for LangGraph integration) ----
def buscar_habilidades_relevantes(retriever):
      def _buscar(state: dict) -> dict:
          plano = state["plano"]
          docs = retriever.invoke_with_filters(plano, filter={"Ano": state["ano"], "Componente": state["componentes"]})
          habilidades_bncc = [{**doc.metadata, "context": doc.page_content} for doc in docs]
          return {
              **state,
              "habilidades_bncc": habilidades_bncc
          }
      return RunnableLambda(_buscar)

# ---- FINAL RUNNABLE ----

def first_check_chain_fn(state: dict) -> dict:
    parsed = first_check_chain.invoke(state)
    return check_first_check_output(parsed, state)

first_check_extractor = RunnableLambda(first_check_chain_fn)