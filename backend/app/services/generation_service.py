import logging
from app.graph.workflow import graph
from app.models.domain import VibeEnum, GenerationResult
from app.models.graph_state import GraphState

logger = logging.getLogger(__name__)


class GenerationService:
    async def generate_carousels(
        self,
        niche: str,
        briefing: str,
        vibe: VibeEnum,
        niche_id: str | None = None,
        vibe_id: str | None = None,
    ) -> dict:
        logger.info(f"Iniciando geração: nicho={niche}, vibe={vibe}")

        initial_state: GraphState = {
            "niche": niche,
            "niche_id": niche_id,
            "briefing": briefing,
            "vibe": vibe,
            "vibe_id": vibe_id,
            "rag_chunks": [],
            "few_shot_examples": [],
            "generator_output": None,
            "generator_attempt": 0,
            "judge_output": None,
            "refine_feedback": [],
            "refine_count": 0,
            "final_result": None,
            "saved_id": None,
            "errors": [],
            "total_tokens_used": 0,
            "cost_usd": 0.0,
        }

        final_state = await graph.ainvoke(initial_state)

        result: GenerationResult | None = final_state.get("final_result")
        options = result.options if result else []

        logger.info(
            f"Geração completa: {len(options)} opções, "
            f"{final_state.get('total_tokens_used', 0)} tokens, "
            f"${final_state.get('cost_usd', 0):.4f}"
        )

        return {
            "options": options,
            "saved_id": final_state.get("saved_id"),
            "metadata": {
                "total_tokens": final_state.get("total_tokens_used", 0),
                "cost_usd": final_state.get("cost_usd", 0.0),
                "refine_attempts": final_state.get("refine_count", 0),
                "judge_score": (
                    final_state["judge_output"].total_score
                    if final_state.get("judge_output")
                    else None
                ),
                "errors": final_state.get("errors", []),
            },
        }
