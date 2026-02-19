from pydantic import BaseModel, Field
from enum import Enum


class VibeEnum(str, Enum):
    EDUCATIVO = "educativo"
    URGENTE = "urgente"
    AUTORIDADE = "autoridade"
    PROVOCATIVO = "provocativo"


class SlideTypeEnum(str, Enum):
    HOOK = "hook"
    DOR = "dor"
    SOLUCAO = "solucao"
    PROVA = "prova"
    BENEFICIO = "beneficio"
    OBJECAO = "objecao"
    CTA = "cta"


class HookTypeEnum(str, Enum):
    PERGUNTA_PROVOCATIVA = "pergunta_provocativa"
    ESTATISTICA_CHOCANTE = "estatistica_chocante"
    DECLARACAO_OUSADA = "declaracao_ousada"
    HISTORIA_PESSOAL = "historia_pessoal"


class Slide(BaseModel):
    slide_number: int = Field(ge=1, le=7)
    type: SlideTypeEnum
    headline: str = Field(min_length=1)
    body: str = ""
    visual_hint: str = ""


class HookAlternative(BaseModel):
    hook_text: str
    hook_style: str
    why_it_works: str


class CarouselOption(BaseModel):
    option_id: int = Field(ge=1, le=3)
    hook_type: str
    hook_alternatives: list[HookAlternative] = Field(default_factory=list)
    slides: list[Slide] = Field(min_length=7, max_length=7)


class GenerationResult(BaseModel):
    options: list[CarouselOption] = Field(min_length=3, max_length=3)
    reasoning: str | None = None


class JudgeScore(BaseModel):
    criterion: str
    score: int = Field(ge=0, le=2)
    feedback: str


class JudgeOutput(BaseModel):
    approved: bool
    total_score: int = Field(ge=0, le=10)
    scores: list[JudgeScore]
    overall_feedback: str
