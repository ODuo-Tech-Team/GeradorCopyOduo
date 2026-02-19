import { z } from "zod";

export const SlideSchema = z.object({
  slide_number: z.number().min(1).max(7),
  type: z.enum(["hook", "dor", "solucao", "prova", "beneficio", "objecao", "cta"]),
  headline: z.string(),
  body: z.string(),
  visual_hint: z.string(),
});

export const HookAlternativeSchema = z.object({
  hook_text: z.string(),
  hook_style: z.string(),
  why_it_works: z.string(),
});

export const CarouselOptionSchema = z.object({
  option_id: z.number(),
  hook_type: z.string(),
  hook_alternatives: z.array(HookAlternativeSchema).optional().default([]),
  slides: z.array(SlideSchema).length(7),
});

export const GenerationResultSchema = z.object({
  options: z.array(CarouselOptionSchema).length(3),
});

export type Slide = z.infer<typeof SlideSchema>;
export type HookAlternative = z.infer<typeof HookAlternativeSchema>;
export type CarouselOption = z.infer<typeof CarouselOptionSchema>;
export type GenerationResult = z.infer<typeof GenerationResultSchema>;

export interface EditableSlide extends Slide {
  isEdited: boolean;
  originalContent?: { headline: string; body: string };
}

export interface CarouselOptionWithMeta extends Omit<CarouselOption, "slides"> {
  slides: EditableSlide[];
  isWinner?: boolean;
}
