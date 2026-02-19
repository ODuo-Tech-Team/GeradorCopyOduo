import logging
from app.models.graph_state import GraphState
from app.rag.retriever import retrieve_context, retrieve_winners

logger = logging.getLogger(__name__)


async def rag_search_node(state: GraphState) -> dict:
    """Nó 2: Busca RAG — contexto + exemplos vencedores."""
    logger.info(f"RAG Search: nicho={state['niche']}, briefing={state['briefing'][:50]}...")

    try:
        # Busca global em todos os docs (sem filtro de nicho)
        chunks = await retrieve_context(
            query=state["briefing"],
            niche_id=None,
            top_k=5,
        )
        winners = await retrieve_winners(
            niche_id=None,
            vibe_id=None,
            top_k=3,
        )
        logger.info(f"RAG: {len(chunks)} chunks, {len(winners)} winners")
        return {
            "rag_chunks": [c.get("chunk_text", c.get("content", "")) for c in chunks],
            "few_shot_examples": winners,
            "generator_attempt": 0,
            "refine_count": 0,
            "total_tokens_used": 0,
            "cost_usd": 0.0,
        }
    except Exception as e:
        logger.error(f"RAG search falhou: {e}", exc_info=True)
        return {
            "rag_chunks": [],
            "few_shot_examples": [],
            "errors": [f"RAG error: {e}"],
            "generator_attempt": 0,
            "refine_count": 0,
            "total_tokens_used": 0,
            "cost_usd": 0.0,
        }
