import logging
from uuid import uuid4
from app.models.graph_state import GraphState
from app.rag.vector_store import save_generation_result

logger = logging.getLogger(__name__)


async def output_node(state: GraphState) -> dict:
    """Nó 6: Output — salva resultado e retorna."""
    logger.info("Output: finalizando geração")

    generator_output = state.get("generator_output")
    if not generator_output or not generator_output.options:
        logger.error("Sem output válido para salvar")
        return {
            "final_result": None,
            "saved_id": None,
            "errors": ["Sem output válido para salvar"],
        }

    try:
        saved_id = str(uuid4())
        await save_generation_result(
            generation_id=saved_id,
            niche=state["niche"],
            niche_id=state.get("niche_id"),
            vibe_id=state.get("vibe_id"),
            briefing=state["briefing"],
            vibe=state["vibe"],
            result=generator_output,
            judge_score=state["judge_output"].total_score if state.get("judge_output") else None,
            refine_count=state.get("refine_count", 0),
            tokens_used=state.get("total_tokens_used", 0),
        )
        logger.info(f"Salvo: {saved_id} com {len(generator_output.options)} opções")
        return {"final_result": generator_output, "saved_id": saved_id}
    except Exception as e:
        logger.error(f"Erro ao salvar: {e}", exc_info=True)
        return {
            "final_result": generator_output,
            "saved_id": None,
            "errors": [f"Save error: {e}"],
        }
