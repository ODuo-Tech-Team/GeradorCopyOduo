import logging
from app.models.graph_state import GraphState
from app.agents.generator_agent import GeneratorAgent
from app.utils.token_counter import estimate_cost

logger = logging.getLogger(__name__)


async def generator_node(state: GraphState) -> dict:
    """Nó 3: Agente Gerador — cria 3 opções de carrossel."""
    attempt = state.get("generator_attempt", 0) + 1
    logger.info(f"Generator: tentativa {attempt}")

    try:
        agent = GeneratorAgent()
        refine_feedback = state.get("refine_feedback", [])
        last_feedback = refine_feedback[-1] if refine_feedback else None

        output, tokens = await agent.generate(
            niche=state["niche"],
            briefing=state["briefing"],
            vibe=state["vibe"],
            rag_chunks=state.get("rag_chunks", []),
            few_shot_examples=state.get("few_shot_examples", []),
            previous_feedback=last_feedback,
        )

        cost = estimate_cost(tokens, model="gpt-4o-mini")
        logger.info(f"Generator: {len(output.options)} opções, {tokens} tokens, ${cost:.4f}")

        return {
            "generator_output": output,
            "generator_attempt": attempt,
            "total_tokens_used": state.get("total_tokens_used", 0) + tokens,
            "cost_usd": state.get("cost_usd", 0.0) + cost,
        }
    except Exception as e:
        logger.error(f"Generator falhou: {e}", exc_info=True)
        return {
            "generator_output": None,
            "generator_attempt": attempt,
            "errors": [f"Generator error: {e}"],
        }
