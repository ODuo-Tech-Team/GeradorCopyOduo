"use client";
import { use, useEffect, useState } from "react";
import { useEditorStore } from "@/lib/store/editor-store";
import { CarouselPreview } from "@/components/results/carousel-preview";
import { apiRequest } from "@/lib/api/client";
import { API_CONFIG } from "@/config/api";
import { Loader2 } from "lucide-react";
import type { Generation } from "@/types/generation";
import type { CarouselOptionWithMeta } from "@/types/carousel";

export default function ResultsPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { options, loadGeneration } = useEditorStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (options.length > 0) {
      setLoading(false);
      return;
    }

    apiRequest<Generation>(`${API_CONFIG.endpoints.generation}/${id}`)
      .then((gen) => {
        const optionsWithMeta: CarouselOptionWithMeta[] = gen.options.map((opt) => ({
          ...opt,
          slides: opt.slides.map((s) => ({ ...s, isEdited: false })),
          isWinner: false,
        }));
        loadGeneration(gen.id, optionsWithMeta);
      })
      .catch((err) => {
        console.error("Erro ao buscar geração:", err);
        setError("Não foi possível carregar os resultados.");
      })
      .finally(() => setLoading(false));
  }, [id, options.length, loadGeneration]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-zinc-500" />
      </div>
    );
  }

  if (error || options.length === 0) {
    return (
      <div className="text-center py-20">
        <p className="text-zinc-500">{error || "Nenhum resultado encontrado"}</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold text-white mb-2">Resultados</h1>
        <p className="text-zinc-500">3 opções de carrossel geradas. Edite, copie e marque a vencedora.</p>
      </div>
      <div className="space-y-8">
        {options.map((option) => (
          <CarouselPreview key={option.option_id} option={option} />
        ))}
      </div>
    </div>
  );
}
