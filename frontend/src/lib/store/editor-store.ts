"use client";
import { create } from "zustand";
import type { CarouselOptionWithMeta, EditableSlide } from "@/types/carousel";

interface EditorState {
  generationId: string | null;
  options: CarouselOptionWithMeta[];
  loadGeneration: (id: string, options: CarouselOptionWithMeta[]) => void;
  updateSlide: (optionId: number, slideNumber: number, updates: Partial<EditableSlide>) => void;
  markAsWinner: (optionId: number) => void;
  resetEdits: (optionId: number, slideNumber: number) => void;
}

export const useEditorStore = create<EditorState>()((set) => ({
  generationId: null,
  options: [],

  loadGeneration: (id, options) => set({ generationId: id, options }),

  updateSlide: (optionId, slideNumber, updates) =>
    set((state) => ({
      options: state.options.map((opt) =>
        opt.option_id === optionId
          ? {
              ...opt,
              slides: opt.slides.map((s) =>
                s.slide_number === slideNumber
                  ? {
                      ...s,
                      ...updates,
                      isEdited: true,
                      originalContent: s.originalContent || { headline: s.headline, body: s.body },
                    }
                  : s
              ),
            }
          : opt
      ),
    })),

  markAsWinner: (optionId) =>
    set((state) => ({
      options: state.options.map((opt) => ({ ...opt, isWinner: opt.option_id === optionId })),
    })),

  resetEdits: (optionId, slideNumber) =>
    set((state) => ({
      options: state.options.map((opt) =>
        opt.option_id === optionId
          ? {
              ...opt,
              slides: opt.slides.map((s) =>
                s.slide_number === slideNumber && s.originalContent
                  ? { ...s, headline: s.originalContent.headline, body: s.originalContent.body, isEdited: false, originalContent: undefined }
                  : s
              ),
            }
          : opt
      ),
    })),
}));
