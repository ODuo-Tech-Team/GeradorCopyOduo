from langgraph.graph import StateGraph, END
from app.models.graph_state import GraphState
from app.graph.nodes.rag_search import rag_search_node
from app.graph.nodes.generator import generator_node
from app.graph.nodes.judge import judge_node
from app.graph.nodes.refine import refine_node
from app.graph.nodes.output import output_node
from app.config import get_settings

settings = get_settings()


def should_refine(state: GraphState) -> str:
    """Decisão condicional: aprovado ou refinar."""
    judge_output = state.get("judge_output")
    refine_count = state.get("refine_count", 0)

    if not judge_output:
        return "output"

    if judge_output.approved:
        return "output"

    if refine_count >= settings.max_refine_attempts:
        return "output"

    return "refine"


def create_workflow() -> StateGraph:
    """
    Cria o workflow LangGraph completo.

    Fluxo:
    RAG Search → Generator → Judge → (approved?) → Output
                                  → (rejected?) → Refine → Generator (loop)
    """
    workflow = StateGraph(GraphState)

    workflow.add_node("rag_search", rag_search_node)
    workflow.add_node("generator", generator_node)
    workflow.add_node("judge", judge_node)
    workflow.add_node("refine", refine_node)
    workflow.add_node("output", output_node)

    workflow.set_entry_point("rag_search")
    workflow.add_edge("rag_search", "generator")
    workflow.add_edge("generator", "judge")

    workflow.add_conditional_edges(
        "judge",
        should_refine,
        {"refine": "refine", "output": "output"},
    )

    workflow.add_edge("refine", "generator")
    workflow.add_edge("output", END)

    return workflow.compile()


graph = create_workflow()
