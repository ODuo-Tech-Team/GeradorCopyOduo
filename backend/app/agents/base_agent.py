import logging
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class BaseAgent:
    def __init__(self, model: str, temperature: float = 0.7):
        self.client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.openai_timeout,
        )
        self.model = model
        self.temperature = temperature

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True,
    )
    async def _call_openai(
        self,
        messages: list[dict],
        response_format: dict | None = None,
    ) -> tuple[str, int]:
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }
        if response_format:
            kwargs["response_format"] = response_format

        logger.debug(f"Calling {self.model} with {len(messages)} messages")
        response = await self.client.chat.completions.create(**kwargs)

        content = response.choices[0].message.content
        tokens = response.usage.total_tokens

        logger.info(f"[{self.model}] {tokens} tokens used")
        return content, tokens
