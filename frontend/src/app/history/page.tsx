"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { StatusBadge } from "@/components/shared/status-badge";
import { apiRequest } from "@/lib/api/client";
import { API_CONFIG } from "@/config/api";
import Link from "next/link";
import { Loader2 } from "lucide-react";

interface HistoryGeneration {
  id: string;
  briefing_text: string;
  niche_id: string | null;
  vibe_id: string | null;
  status: string;
  score: number | null;
  created_at: string;
}

export default function HistoryPage() {
  const router = useRouter();
  const [generations, setGenerations] = useState<HistoryGeneration[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiRequest<HistoryGeneration[]>(API_CONFIG.endpoints.history)
      .then(setGenerations)
      .catch((err) => console.error("Erro ao buscar histórico:", err))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-zinc-500" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl md:text-4xl font-bold text-white">Histórico</h1>
        <p className="text-zinc-500 mt-1 text-sm md:text-base">Todas as gerações de carrosséis</p>
      </div>

      {generations.length === 0 ? (
        <div className="text-center py-20 border border-zinc-800 rounded-xl">
          <p className="text-zinc-500">Nenhuma geração ainda. Comece gerando sua primeira copy!</p>
          <Link href="/generate" className="text-blue-500 hover:underline mt-2 inline-block">
            Gerar Copy
          </Link>
        </div>
      ) : (
        <>
          {/* Desktop table */}
          <div className="hidden md:block border border-zinc-800 rounded-xl overflow-hidden">
            <table className="w-full">
              <thead className="bg-zinc-900">
                <tr>
                  <th className="px-4 py-3 text-left text-xs text-zinc-500">Data</th>
                  <th className="px-4 py-3 text-left text-xs text-zinc-500">Briefing</th>
                  <th className="px-4 py-3 text-left text-xs text-zinc-500">Status</th>
                  <th className="px-4 py-3 text-left text-xs text-zinc-500">Score</th>
                </tr>
              </thead>
              <tbody>
                {generations.map((g) => (
                  <tr
                    key={g.id}
                    onClick={() => router.push(`/results/${g.id}`)}
                    className="border-t border-zinc-800 hover:bg-zinc-900/50 cursor-pointer transition-colors"
                  >
                    <td className="px-4 py-3 text-sm text-zinc-300 whitespace-nowrap">
                      {new Date(g.created_at).toLocaleDateString("pt-BR")}
                    </td>
                    <td className="px-4 py-3 text-sm text-zinc-300 max-w-xs truncate">
                      {g.briefing_text?.slice(0, 80) ?? "-"}
                    </td>
                    <td className="px-4 py-3"><StatusBadge status={g.status} /></td>
                    <td className="px-4 py-3 text-sm text-zinc-300">{g.score ?? "-"}/10</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Mobile card list */}
          <div className="md:hidden space-y-3">
            {generations.map((g) => (
              <div
                key={g.id}
                onClick={() => router.push(`/results/${g.id}`)}
                className="border border-zinc-800 rounded-xl p-4 active:bg-zinc-900/50 cursor-pointer transition-colors"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-zinc-500">
                    {new Date(g.created_at).toLocaleDateString("pt-BR")}
                  </span>
                  <div className="flex items-center gap-2">
                    <StatusBadge status={g.status} />
                    <span className="text-xs text-zinc-400">{g.score ?? "-"}/10</span>
                  </div>
                </div>
                <p className="text-sm text-zinc-300 line-clamp-2">
                  {g.briefing_text?.slice(0, 120) ?? "-"}
                </p>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
