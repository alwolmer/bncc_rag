from langgraph.graph import StateGraph, Graph, END
from typing import TypedDict, Optional, List, Dict, Any
from .first_check import buscar_habilidades_relevantes, first_check_extractor
from .avaliacao import avaliar_plano_chain

class SubtopicoEstrutura(TypedDict):
    presente: bool
    adequado: bool
    identificacao: Optional[str]
    sugestao_melhoria: Optional[str]

class EstadoPlano(TypedDict):
    plano: str
    etapa: str
    ano: Optional[str]
    componentes: List[str]
    habilidades_bncc: List[Dict[str, Any]]
    plano_ok: bool
    habilidades_ok: bool
    codigos_bncc: List[str]
    avaliacao_estrutura: Dict[str, SubtopicoEstrutura]
    avaliacao_estilo: str
    avaliacao_conteudo: str
    status: str
    tempo: SubtopicoEstrutura
    status: str
    error: str
    human_message: Optional[str]

# --- Função para construir o grafo ---
def create_chain_graph(retriever) -> Graph:
    workflow = StateGraph(EstadoPlano)

    workflow.add_node("buscar_habilidades", buscar_habilidades_relevantes(retriever))
    workflow.add_node("first_check", first_check_extractor)
    workflow.add_node("avaliar_plano", avaliar_plano_chain)
    
    # Add end node
    def end_node(state: EstadoPlano) -> EstadoPlano:
        return state
    
    workflow.add_node("end", end_node)

    # Add edges
    workflow.add_edge("buscar_habilidades", "first_check")
    # workflow.add_edge("first_check", "avaliar_plano")

    # Set entry point
    workflow.set_entry_point("buscar_habilidades")

    # Set conditional edges
    def should_continue(state: EstadoPlano) -> str:
        if not state["plano_ok"] or not state["habilidades_ok"]:
            return "end"
        return "avaliar_plano"

    workflow.add_conditional_edges(
        "first_check",
        should_continue,
        {
            "avaliar_plano": "avaliar_plano",
            "end": "end"
        }
    )

    # Compile the graph
    chain = workflow.compile()

    return chain

def run_chain(chain: Graph, plano: str, etapa: str, ano: str, componentes: list) -> Dict:
    """Run the chain with the given inputs."""
    initial_state = {
        "plano": plano,
        "etapa": etapa,
        "ano": ano,
        "componentes": componentes,
        "habilidades_bncc": [],
        "plano_ok": False,
        "habilidades_ok": False,
        "codigos_bncc": [],
        "avaliacao_estrutura": {
            "objetivos": {"presente": False, "adequado": False, "identificacao": None, "sugestao_melhoria": None},
            "conteudos": {"presente": False, "adequado": False, "identificacao": None, "sugestao_melhoria": None},
            "metodologia": {"presente": False, "adequado": False, "identificacao": None, "sugestao_melhoria": None},
            "avaliacao": {"presente": False, "adequado": False, "identificacao": None, "sugestao_melhoria": None},
            "recursos": {"presente": False, "adequado": False, "identificacao": None, "sugestao_melhoria": None},
            "materiais": {"presente": False, "adequado": False, "identificacao": None, "sugestao_melhoria": None},
            "tempo": {"presente": False, "adequado": False, "identificacao": None, "sugestao_melhoria": None},
        },
        
        "status": "pending",
        "error": "",
        "human_message": None
    }

    try:
        result = chain.invoke(initial_state)
        result["status"] = "success"
        return result
    except Exception as e:
        return {
            **initial_state,
            "status": "error",
            "error": str(e)
        }