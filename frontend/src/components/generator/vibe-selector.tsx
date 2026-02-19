"use client";
import { VIBES } from "@/config/constants";
import { cn } from "@/lib/utils";
import type { Vibe } from "@/types/generation";

interface Props {
  value: Vibe | null;
  onChange: (v: Vibe) => void;
}

export function VibeSelector({ value, onChange }: Props) {
  return (
    <div className="space-y-3">
      <label className="text-sm font-medium text-zinc-300">Tom da Copy</label>
      <div className="grid grid-cols-2 gap-3">
        {VIBES.map((v) => (
          <button
            key={v.value}
            type="button"
            onClick={() => onChange(v.value as Vibe)}
            className={cn(
              "p-4 border-2 rounded-xl text-left transition-all",
              "hover:border-blue-500 hover:shadow-md",
              value === v.value ? "border-blue-500 bg-blue-500/10" : "border-zinc-700 bg-zinc-800/50"
            )}
          >
            <div className="font-semibold text-white">{v.label}</div>
            <div className="text-xs text-zinc-400 mt-1">{v.description}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
