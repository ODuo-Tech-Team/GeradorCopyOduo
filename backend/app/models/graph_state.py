from typing import TypedDict, Annotated
from operator import add
from app.models.domain import GenerationResult, JudgeOutput, CarouselOption, VibeEnum


class GraphState(TypedDict):
    # Input
    niche: str
    niche_id: str | None
    briefing: str
    vibe: VibeEnum
    vibe_id: str | None

    # RAG
    rag_chunks: list[str]
    few_shot_examples: list[dict]

    # Generator
    generator_output: GenerationResult | None
    generator_attempt: int

    # Judge
    judge_output: JudgeOutput | None

    # Refine loop
    refine_feedback: Annotated[list[str], add]
    refine_count: int

    # Final
    final_result: GenerationResult | None
    saved_id: str | None

    # Tracking
    errors: Annotated[list[str], add]
    total_tokens_used: int
    cost_usd: float
