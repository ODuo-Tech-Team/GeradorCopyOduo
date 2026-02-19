"use client";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Lightbulb, Loader2, ChevronDown, ChevronUp, Newspaper } from "lucide-react";
import { apiRequest } from "@/lib/api/client";
import { API_CONFIG } from "@/config/api";
import { cn } from "@/lib/utils";

interface BriefingIdea {
  title: string;
  description: string;
}

interface BriefingIdeasResponse {
  ideas: BriefingIdea[];
}

interface BriefingIdeasProps {
  niche: string;
  onSelectIdea: (description: string) => void;
}

export function BriefingIdeas({ niche, onSelectIdea }: BriefingIdeasProps) {
  const [expanded, setExpanded] = useState(false);
  const [newsContext, setNewsContext] = useState("");
  const [ideas, setIdeas] = useState<BriefingIdea[]>([]);
  const [loading, setLoading] = useState(false);
  const [showNewsInput, setShowNewsInput] = useState(false);

  const handleGenerateIdeas = async () => {
    if (!niche) return;
    setLoading(true);
    try {
      const result = await apiRequest<BriefingIdeasResponse>(API_CONFIG.endpoints.briefingIdeas, {
        method: "POST",
        body: JSON.stringify({ niche, context: newsContext }),
      });
      setIdeas(result.ideas);
    } catch (err) {
      console.error("Erro ao gerar ideias:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="border border-zinc-800 rounded-xl overflow-hidden">
      <button
        type="button"
        onClick={() => setExpanded(!expanded)}
        className="w-full flex items-center justify-between p-4 hover:bg-zinc-800/30 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Lightbulb className="h-4 w-4 text-amber-400" />
          <span className="text-sm font-medium text-zinc-300">Ideias para Briefing</span>
        </div>
        {expanded ? <ChevronUp className="h-4 w-4 text-zinc-500" /> : <ChevronDown className="h-4 w-4 text-zinc-500" />}
      </button>

      {expanded && (
        <div className="p-4 pt-0 space-y-4">
          <p className="text-xs text-zinc-500">
            Gere ideias baseadas no nicho selecionado. Opcionalmente, cole uma notícia para extrair ângulos de marketing.
          </p>

          <button
            type="button"
            onClick={() => setShowNewsInput(!showNewsInput)}
            className="flex items-center gap-2 text-xs text-blue-400 hover:text-blue-300 transition-colors"
          >
            <Newspaper className="h-3 w-3" />
            {showNewsInput ? "Esconder campo de notícia" : "Colar uma notícia / artigo"}
          </button>

          {showNewsInput && (
            <Textarea
              value={newsContext}
              onChange={(e) => setNewsContext(e.target.value)}
              placeholder="Cole aqui uma notícia, artigo ou texto para a IA extrair ideias de conteúdo..."
              rows={4}
              className="resize-none text-sm"
              maxLength={5000}
            />
          )}

          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={handleGenerateIdeas}
            disabled={!niche || loading}
          >
            {loading ? (
              <>
                <Loader2 className="mr-2 h-3 w-3 animate-spin" />
                Gerando ideias...
              </>
            ) : (
              <>
                <Lightbulb className="mr-2 h-3 w-3" />
                Gerar Ideias {newsContext ? "da Notícia" : "para o Nicho"}
              </>
            )}
          </Button>

          {ideas.length > 0 && (
            <div className="grid grid-cols-1 gap-2">
              {ideas.map((idea, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => onSelectIdea(idea.description)}
                  className={cn(
                    "text-left border border-zinc-700 rounded-lg p-3 space-y-1",
                    "hover:border-blue-500/50 hover:bg-blue-500/5 transition-colors cursor-pointer"
                  )}
                >
                  <p className="text-sm font-medium text-white">{idea.title}</p>
                  <p className="text-xs text-zinc-400">{idea.description}</p>
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
