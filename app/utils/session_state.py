import streamlit as st
from typing import Any, Dict, List, Optional

def init_session_state(key: str, default: Any) -> None:
    """Initialize a session state variable if it doesn't exist."""
    if key not in st.session_state:
        st.session_state[key] = default

def update_session_state(updates: Dict[str, Any]) -> None:
    """Update multiple session state variables at once."""
    st.session_state.update(updates)

# Application State
def init_app_state() -> None:
    """Initialize application-wide state variables."""
    init_session_state("access_logged", False)
    init_session_state("db_conn", None)
    init_session_state("embeddings", None)
    init_session_state("vector_store_fund", None)
    init_session_state("vector_store_em", None)

# Search State
def init_search_state() -> None:
    """Initialize search-related state variables."""
    init_session_state("plano", "")
    init_session_state("resultados", [])
    init_session_state("codigos_resultados", [])
    init_session_state("ensino_medio", False)
    init_session_state("filtros", {})
    init_session_state("update_busca", False)

# UI State
def init_ui_state() -> None:
    """Initialize UI-related state variables."""
    init_session_state("feedback_enviado", False)
    init_session_state("selecionados", [])
    init_session_state("selecionados_df", None)
    init_session_state("limpar", False)

# Initialize all state
def init_all_state() -> None:
    """Initialize all session state variables."""
    init_app_state()
    init_search_state()
    init_ui_state()

# State update helpers
def clear_search() -> None:
    """Clear search-related state."""
    update_session_state({
        "plano": "",
        "resultados": [],
        "codigos_resultados": [],
        "feedback_enviado": False
    })

def update_search_filters(componentes: List[str], anos: List[str], ensino_medio: bool) -> None:
    """Update search filter state."""
    update_session_state({
        "filtros": {
            "componentes": componentes,
            "anos": anos
        },
        "ensino_medio": ensino_medio
    }) 