import logging
from app.models.graph_state import GraphState

logger = logging.getLogger(__name__)


async def refine_node(state: GraphState) -> dict:
    """Nó 5: Refine — prepara feedback para nova tentativa."""
    judge_output = state.get("judge_output")
    refine_count = state.get("refine_count", 0) + 1

    logger.info(f"Refine: iteração {refine_count}")

    if not judge_output:
        return {"refine_count": refine_count}

    feedback_text = f"""MOTIVO DA REJEIÇÃO (Score: {judge_output.total_score}/10 — Precisa >= 8)

{judge_output.overall_feedback}

SCORES DETALHADOS:
{chr(10).join(f"- {s.criterion}: {s.score}/2 — {s.feedback}" for s in judge_output.scores)}

MUDANÇAS OBRIGATÓRIAS:
{chr(10).join(f"- {s.feedback}" for s in judge_output.scores if s.score < 2)}
"""

    logger.info(f"Refine: feedback preparado ({len(feedback_text)} chars)")
    return {
        "refine_feedback": [feedback_text],
        "refine_count": refine_count,
    }
