"use client";
import { use, useEffect, useState } from "react";
import { useEditorStore } from "@/lib/store/editor-store";
import { CarouselPreview } from "@/components/results/carousel-preview";
import { Loader2 } from "lucide-react";

export default function ResultsClient({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { options } = useEditorStore();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(false);
  }, [id]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-zinc-500" />
      </div>
    );
  }

  if (options.length === 0) {
    return (
      <div className="text-center py-20">
        <p className="text-zinc-500">Nenhum resultado encontrado</p>
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
