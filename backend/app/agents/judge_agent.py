import json
import logging
from app.agents.base_agent import BaseAgent
from app.models.domain import JudgeOutput, GenerationResult, VibeEnum
from app.graph.prompts.judge_prompt import build_judge_prompt
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class JudgeAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            model=settings.judge_model,
            temperature=settings.temperature_judge,
        )

    async def evaluate(
        self,
        generator_output: GenerationResult,
        briefing: str,
        niche: str,
        vibe: VibeEnum,
    ) -> tuple[JudgeOutput, int]:
        messages = build_judge_prompt(
            generator_output=generator_output.model_dump(),
            briefing=briefing,
            niche=niche,
            vibe=vibe.value,
        )

        response_text, tokens = await self._call_openai(
            messages=messages,
            response_format={"type": "json_object"},
        )

        try:
            data = json.loads(response_text)
            output = JudgeOutput.model_validate(data)

            # Enforce approval logic
            output.approved = output.total_score >= settings.judge_pass_score

            logger.info(f"Judge: score={output.total_score}, approved={output.approved}")
            return output, tokens
        except Exception as e:
            logger.error(f"Falha ao parsear output do judge: {e}")
            raise ValueError(f"Judge produziu JSON inválido: {e}")
