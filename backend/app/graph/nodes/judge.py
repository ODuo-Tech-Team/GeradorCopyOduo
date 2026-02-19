import logging
from app.models.graph_state import GraphState
from app.agents.judge_agent import JudgeAgent
from app.utils.token_counter import estimate_cost

logger = logging.getLogger(__name__)


async def judge_node(state: GraphState) -> dict:
    """Nó 4: Agente Juiz — valida qualidade do output."""
    logger.info("Judge: avaliando output do generator")

    if not state.get("generator_output"):
        logger.warning("Sem output do generator para julgar")
        return {
            "judge_output": None,
            "errors": ["Sem output do generator para julgar"],
        }

    try:
        agent = JudgeAgent()
        output, tokens = await agent.evaluate(
            generator_output=state["generator_output"],
            briefing=state["briefing"],
            niche=state["niche"],
            vibe=state["vibe"],
        )

        cost = estimate_cost(tokens, model="gpt-4o")
        logger.info(f"Judge: score={output.total_score}/10, approved={output.approved}, ${cost:.4f}")

        return {
            "judge_output": output,
            "total_tokens_used": state.get("total_tokens_used", 0) + tokens,
            "cost_usd": state.get("cost_usd", 0.0) + cost,
        }
    except Exception as e:
        logger.error(f"Judge falhou: {e}", exc_info=True)
        return {
            "judge_output": None,
            "errors": [f"Judge error: {e} — aprovando por segurança"],
        }
