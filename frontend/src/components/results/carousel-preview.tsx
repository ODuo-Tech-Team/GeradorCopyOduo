"use client";
import { useEditorStore } from "@/lib/store/editor-store";
import { SlideCard } from "./slide-card";
import { Button } from "@/components/ui/button";
import { Trophy, Copy, Check } from "lucide-react";
import type { CarouselOptionWithMeta } from "@/types/carousel";
import { cn } from "@/lib/utils";
import { useState } from "react";

export function CarouselPreview({ option }: { option: CarouselOptionWithMeta }) {
  const { updateSlide, resetEdits, markAsWinner } = useEditorStore();
  const [copied, setCopied] = useState(false);
  const [hooksCopied, setHooksCopied] = useState(false);

  const handleCopyAll = () => {
    const text = option.slides
      .map((s) => `--- Slide ${s.slide_number} (${s.type}) ---\n${s.headline}\n\n${s.body}`)
      .join("\n\n");
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={cn(
      "border-2 rounded-2xl p-6 space-y-6",
      option.isWinner ? "border-green-500 bg-green-500/5" : "border-zinc-700"
    )}>
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-bold text-white">
            Opção {option.option_id}
            {option.isWinner && <span className="ml-2 text-green-400 text-sm">Vencedora</span>}
          </h3>
          <p className="text-sm text-zinc-500">Hook: {option.hook_type.replace(/_/g, " ")}</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" onClick={handleCopyAll}>
            {copied ? <Check className="mr-2 h-4 w-4 text-green-400" /> : <Copy className="mr-2 h-4 w-4" />}
            {copied ? "Copiado!" : "Copiar Tudo"}
          </Button>
          <Button
            variant={option.isWinner ? "default" : "outline"}
            size="sm"
            onClick={() => markAsWinner(option.option_id)}
          >
            <Trophy className="mr-2 h-4 w-4" />
            {option.isWinner ? "Vencedora" : "Marcar Vencedora"}
          </Button>
        </div>
      </div>

      {option.hook_alternatives && option.hook_alternatives.length > 0 && (
        <div className="bg-zinc-800/50 rounded-xl p-4 space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-semibold text-amber-400 uppercase tracking-wider">Alternativas de Hook</h4>
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                const text = option.hook_alternatives
                  .map((alt, i) => `Hook ${i + 1} (${alt.hook_style.replace(/_/g, " ")}): "${alt.hook_text}"`)
                  .join("\n");
                navigator.clipboard.writeText(text);
                setHooksCopied(true);
                setTimeout(() => setHooksCopied(false), 2000);
              }}
            >
              {hooksCopied ? <Check className="mr-2 h-3 w-3 text-green-400" /> : <Copy className="mr-2 h-3 w-3" />}
              {hooksCopied ? "Copiado!" : "Copiar Hooks"}
            </Button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {option.hook_alternatives.map((alt, idx) => (
              <div key={idx} className="bg-zinc-900/60 border border-zinc-700 rounded-lg p-3 space-y-2">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-amber-400">#{idx + 1}</span>
                  <span className="text-xs text-zinc-500 uppercase">{alt.hook_style.replace(/_/g, " ")}</span>
                </div>
                <p className="text-white font-medium text-sm leading-snug">{alt.hook_text}</p>
                <p className="text-xs text-zinc-400 italic">{alt.why_it_works}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {option.slides.map((slide) => (
          <SlideCard
            key={slide.slide_number}
            slide={slide}
            onEdit={(updates) => updateSlide(option.option_id, slide.slide_number, updates)}
            onReset={() => resetEdits(option.option_id, slide.slide_number)}
          />
        ))}
      </div>
    </div>
  );
}
