"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { NicheSelector } from "./niche-selector";
import { VibeSelector } from "./vibe-selector";
import { BriefingIdeas } from "./briefing-ideas";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Loader2, Sparkles } from "lucide-react";
import { apiRequest } from "@/lib/api/client";
import { API_CONFIG } from "@/config/api";
import { useEditorStore } from "@/lib/store/editor-store";
import type { Vibe, GenerateResponse } from "@/types/generation";
import type { CarouselOptionWithMeta } from "@/types/carousel";

export function GenerationForm() {
  const router = useRouter();
  const { loadGeneration } = useEditorStore();
  const [niche, setNiche] = useState("");
  const [vibe, setVibe] = useState<Vibe | null>(null);
  const [briefing, setBriefing] = useState("");
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState("");

  const isValid = niche && vibe && briefing.length >= 10;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!isValid || !vibe) return;

    setLoading(true);
    setStep("Buscando contexto...");

    try {
      setTimeout(() => setStep("Gerando copys com IA..."), 3000);
      setTimeout(() => setStep("Validando qualidade..."), 8000);
      setTimeout(() => setStep("Finalizando..."), 12000);

      const result = await apiRequest<GenerateResponse>(API_CONFIG.endpoints.generate, {
        method: "POST",
        body: JSON.stringify({ niche, vibe, briefing }),
      });

      if (result.success && result.generation_id) {
        const optionsWithMeta: CarouselOptionWithMeta[] = result.options.map((opt) => ({
          ...opt,
          slides: opt.slides.map((s) => ({ ...s, isEdited: false })),
          isWinner: false,
        }));
        loadGeneration(result.generation_id, optionsWithMeta);
        router.push(`/results/${result.generation_id}`);
      }
    } catch (err) {
      console.error("Erro na geração:", err);
      setStep("");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6 max-w-3xl mx-auto">
      <NicheSelector value={niche} onChange={setNiche} />
      <VibeSelector value={vibe} onChange={setVibe} />

      <BriefingIdeas niche={niche} onSelectIdea={(desc) => setBriefing(desc)} />

      <div className="space-y-3">
        <label className="text-sm font-medium text-zinc-300">Briefing</label>
        <Textarea
          value={briefing}
          onChange={(e) => setBriefing(e.target.value)}
          placeholder="Descreva o contexto, público-alvo, pontos-chave a abordar no carrossel..."
          rows={6}
          className="resize-none"
          maxLength={2000}
        />
        <div className="text-xs text-zinc-500 text-right">{briefing.length}/2000</div>
      </div>

      <Button type="submit" disabled={!isValid || loading} className="w-full" size="lg">
        {loading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            {step}
          </>
        ) : (
          <>
            <Sparkles className="mr-2 h-4 w-4" />
            Gerar 3 Opções de Carrossel
          </>
        )}
      </Button>
    </form>
  );
}
