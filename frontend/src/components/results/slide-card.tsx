"use client";
import { useState } from "react";
import { SLIDE_TYPES } from "@/config/constants";
import type { EditableSlide } from "@/types/carousel";
import { cn } from "@/lib/utils";
import { Pencil, Copy, RotateCcw, Check } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Props {
  slide: EditableSlide;
  onEdit: (updates: Partial<EditableSlide>) => void;
  onReset: () => void;
}

export function SlideCard({ slide, onEdit, onReset }: Props) {
  const [editing, setEditing] = useState(false);
  const [copied, setCopied] = useState(false);
  const config = SLIDE_TYPES[slide.type] || { label: slide.type, color: "bg-zinc-500" };

  const handleCopy = () => {
    navigator.clipboard.writeText(`${slide.headline}\n\n${slide.body}`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div
      className={cn(
        "relative group border-2 rounded-xl p-5 transition-all min-h-[180px]",
        "hover:shadow-lg hover:shadow-zinc-900/50",
        editing ? "border-blue-500" : "border-zinc-700",
        slide.isEdited && "ring-2 ring-yellow-500/50"
      )}
    >
      <div className={cn("inline-block px-2.5 py-1 rounded-full text-xs font-semibold mb-3 text-white", config.color)}>
        {slide.slide_number}. {config.label}
      </div>

      {editing ? (
        <div className="space-y-2">
          <input
            type="text"
            value={slide.headline}
            onChange={(e) => onEdit({ headline: e.target.value })}
            className="w-full bg-zinc-800 border border-zinc-600 rounded px-3 py-2 text-lg font-bold text-white"
          />
          <textarea
            value={slide.body}
            onChange={(e) => onEdit({ body: e.target.value })}
            className="w-full bg-zinc-800 border border-zinc-600 rounded px-3 py-2 text-sm text-zinc-300 resize-none"
            rows={3}
          />
          <Button size="sm" variant="ghost" onClick={() => setEditing(false)}>
            <Check className="h-3 w-3 mr-1" /> Salvar
          </Button>
        </div>
      ) : (
        <div className="space-y-2">
          <h3 className="text-lg font-bold leading-tight text-white">{slide.headline}</h3>
          {slide.body && <p className="text-sm text-zinc-400">{slide.body}</p>}
          {slide.visual_hint && <p className="text-xs text-zinc-600 italic mt-2">Sugestão visual: {slide.visual_hint}</p>}
        </div>
      )}

      <div className="absolute top-3 right-3 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        <Button size="icon" variant="ghost" className="h-7 w-7" onClick={() => setEditing(!editing)}>
          <Pencil className="h-3 w-3" />
        </Button>
        <Button size="icon" variant="ghost" className="h-7 w-7" onClick={handleCopy}>
          {copied ? <Check className="h-3 w-3 text-green-400" /> : <Copy className="h-3 w-3" />}
        </Button>
        {slide.isEdited && (
          <Button size="icon" variant="ghost" className="h-7 w-7" onClick={onReset}>
            <RotateCcw className="h-3 w-3" />
          </Button>
        )}
      </div>
    </div>
  );
}
