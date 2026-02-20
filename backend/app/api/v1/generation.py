import json
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.models.requests import GenerateRequest
from app.models.responses import GenerateResponse
from app.services.generation_service import GenerationService
from app.agents.base_agent import BaseAgent
from app.rag.vector_store import list_generations, get_generation_by_id, get_generation_stats

logger = logging.getLogger(__name__)
router = APIRouter()


class BriefingIdeasRequest(BaseModel):
    niche: str
    context: str = ""


class BriefingIdea(BaseModel):
    title: str
    description: str


class BriefingIdeasResponse(BaseModel):
    ideas: list[BriefingIdea]


@router.post("/briefing-ideas", response_model=BriefingIdeasResponse)
async def generate_briefing_ideas(request: BriefingIdeasRequest):
    """Gera ideias de briefing baseadas no nicho e contexto opcional (noticia, artigo, etc)."""
    logger.info(f"POST /briefing-ideas: niche={request.niche}, context_len={len(request.context)}")

    system_prompt = """Você é um estrategista de conteúdo para Instagram da ODuo, uma empresa que faz MARKETING para DONOS DE LOCADORAS.

## CONTEXTO IMPORTANTE:
- A ODuo NÃO é uma locadora. A ODuo faz marketing para locadoras.
- O público-alvo dos carrosséis são os CLIENTES FINAIS das locadoras (quem vai alugar).
- Mas quem CONTRATA a ODuo são os DONOS das locadoras que querem ALUGAR MAIS.
- As ideias de briefing devem ajudar os DONOS DE LOCADORAS a atrair mais clientes e fechar mais locações.

## SUA MISSÃO:
Gerar ideias criativas de briefing para carrosséis de Instagram que ajudem locadoras a ALUGAR MAIS.

## REGRAS:
- Todas as ideias DEVEM ser sobre LOCAÇÃO (alugar, locar), NUNCA sobre compra/venda
- Ideias devem ser específicas e acionáveis, não genéricas
- Pense em dores dos donos de locadoras: baixa demanda, sazonalidade, concorrência, clientes que preferem comprar, objeções de preço
- Pense em conteúdos que ATRAIAM clientes para as locadoras: benefícios de alugar vs comprar, economia, praticidade, flexibilidade
- Cada ideia deve ter um título curto (max 10 palavras) e uma descrição detalhada (2-3 frases) explicando o ângulo do conteúdo e como isso ajuda a locadora a alugar mais
- Gere entre 5 e 8 ideias variadas
- Se um contexto/notícia for fornecido, extraia ângulos de marketing que uma LOCADORA pode usar para atrair clientes

## FORMATO DE SAÍDA (JSON estrito):
{
  "ideas": [
    {"title": "Título curto da ideia", "description": "Descrição detalhada do ângulo e como isso ajuda a locadora a alugar mais"}
  ]
}"""

    user_parts = [f"NICHO DA LOCADORA: {request.niche}"]
    if request.context.strip():
        user_parts.append(f"CONTEXTO/NOTÍCIA PARA EXTRAIR ÂNGULOS DE MARKETING PARA LOCADORAS:\n{request.context}")
    else:
        user_parts.append("Gere ideias de conteúdo que ajudem locadoras deste nicho a atrair mais clientes e alugar mais.")
    user_parts.append("Retorne APENAS o JSON, sem texto adicional.")

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "\n\n".join(user_parts)},
    ]

    try:
        agent = BaseAgent(model="gpt-4o-mini", temperature=0.9)
        response_text, _ = await agent._call_openai(
            messages=messages,
            response_format={"type": "json_object"},
        )
        data = json.loads(response_text)
        return BriefingIdeasResponse(**data)
    except Exception as e:
        logger.error(f"Erro ao gerar ideias: {e}", exc_info=True)
        raise HTTPException(500, f"Erro ao gerar ideias: {e}")


@router.post("/", response_model=GenerateResponse)
async def generate_carousels(request: GenerateRequest):
    """Gera 3 opções de carrossel (7 slides cada) para o mercado de locação."""
    logger.info(f"POST /generate: niche={request.niche}, vibe={request.vibe}")

    try:
        service = GenerationService()
        result = await service.generate_carousels(
            niche=request.niche,
            briefing=request.briefing,
            vibe=request.vibe,
            niche_id=request.niche_id,
            vibe_id=request.vibe_id,
        )

        if not result["options"]:
            raise HTTPException(500, "Falha ao gerar carrosséis válidos")

        return GenerateResponse(
            success=True,
            generation_id=result["saved_id"] or "not-saved",
            options=result["options"],
            metadata=result["metadata"],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro na geração: {e}", exc_info=True)
        raise HTTPException(500, f"Erro na geração: {e}")


@router.get("/history")
async def get_history(limit: int = 50, offset: int = 0):
    """Lista as gerações com status e score."""
    try:
        generations = await list_generations(limit=limit, offset=offset)
        for g in generations:
            feedback = g.get("judge_feedback")
            g["score"] = feedback.get("score") if feedback else None
        return generations
    except Exception as e:
        logger.error(f"Erro ao listar histórico: {e}", exc_info=True)
        raise HTTPException(500, f"Erro ao buscar histórico: {e}")


@router.get("/stats")
async def get_stats():
    """Retorna contagens para o dashboard."""
    try:
        return await get_generation_stats()
    except Exception as e:
        logger.error(f"Erro ao buscar stats: {e}", exc_info=True)
        raise HTTPException(500, f"Erro ao buscar stats: {e}")


@router.get("/{generation_id}")
async def get_generation(generation_id: str):
    """Retorna uma geração completa por ID (com options)."""
    try:
        gen = await get_generation_by_id(generation_id)
        if not gen:
            raise HTTPException(404, "Geração não encontrada")
        return gen
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao buscar geração {generation_id}: {e}", exc_info=True)
        raise HTTPException(500, f"Erro ao buscar geração: {e}")
