import json
import logging
from app.agents.base_agent import BaseAgent
from app.models.domain import GenerationResult, VibeEnum
from app.graph.prompts.generator_prompt import build_generator_prompt
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class GeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            model=settings.generator_model,
            temperature=settings.temperature_generator,
        )

    async def generate(
        self,
        niche: str,
        briefing: str,
        vibe: VibeEnum,
        rag_chunks: list[str],
        few_shot_examples: list[dict],
        previous_feedback: str | None = None,
    ) -> tuple[GenerationResult, int]:
        messages = build_generator_prompt(
            niche=niche,
            briefing=briefing,
            vibe=vibe,
            rag_chunks=rag_chunks,
            few_shot_examples=few_shot_examples,
            previous_feedback=previous_feedback,
        )

        response_text, tokens = await self._call_openai(
            messages=messages,
            response_format={"type": "json_object"},
        )

        try:
            data = json.loads(response_text)
            output = GenerationResult.model_validate(data)
            logger.info(f"Generator: {len(output.options)} opções criadas")
            return output, tokens
        except Exception as e:
            logger.error(f"Falha ao parsear output do generator: {e}")
            raise ValueError(f"Generator produziu JSON inválido: {e}")
