import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from openai import APIError, RateLimitError, APITimeoutError

logger = logging.getLogger(__name__)


def setup_error_handlers(app: FastAPI):
    @app.exception_handler(APIError)
    async def openai_api_error(request: Request, exc: APIError):
        logger.error(f"OpenAI API error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"error": "OpenAI API error", "detail": str(exc)},
        )

    @app.exception_handler(RateLimitError)
    async def openai_rate_limit(request: Request, exc: RateLimitError):
        logger.warning(f"OpenAI rate limit: {exc}")
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"error": "Rate limit", "detail": "Tente novamente em alguns segundos."},
        )

    @app.exception_handler(APITimeoutError)
    async def openai_timeout(request: Request, exc: APITimeoutError):
        logger.error(f"OpenAI timeout: {exc}")
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={"error": "Timeout", "detail": "OpenAI demorou demais. Tente novamente."},
        )

    @app.exception_handler(Exception)
    async def global_error(request: Request, exc: Exception):
        logger.error(f"Erro: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "Erro interno", "detail": str(exc)},
        )
