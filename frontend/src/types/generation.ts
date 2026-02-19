import type { CarouselOption } from "./carousel";

export type Vibe = "educativo" | "urgente" | "autoridade" | "provocativo";

export interface GenerationRequest {
  niche: string;
  briefing: string;
  vibe: Vibe;
  niche_id?: string;
  vibe_id?: string;
}

export interface Generation {
  id: string;
  briefing_text: string;
  niche_name?: string;
  vibe_name?: string;
  status: "generating" | "completed" | "failed";
  options: CarouselOption[];
  judge_feedback?: { score: number };
  retry_count: number;
  tokens_used?: number;
  created_at: string;
}

export interface GenerateResponse {
  success: boolean;
  generation_id: string;
  options: CarouselOption[];
  metadata: {
    total_tokens: number;
    cost_usd: number;
    refine_attempts: number;
    judge_score: number | null;
    errors: string[];
  };
}
