"use client";
import { StatusBadge } from "@/components/shared/status-badge";
import Link from "next/link";

export default function HistoryPage() {
  // Placeholder — integrar com Supabase
  const generations: Array<{
    id: string;
    niche: string;
    vibe: string;
    status: string;
    score: number | null;
    created_at: string;
  }> = [];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold text-white">Histórico</h1>
        <p className="text-zinc-500 mt-1">Todas as gerações de carrosséis</p>
      </div>

      {generations.length === 0 ? (
        <div className="text-center py-20 border border-zinc-800 rounded-xl">
          <p className="text-zinc-500">Nenhuma geração ainda. Comece gerando sua primeira copy!</p>
          <Link href="/generate" className="text-blue-500 hover:underline mt-2 inline-block">
            Gerar Copy
          </Link>
        </div>
      ) : (
        <div className="border border-zinc-800 rounded-xl overflow-hidden">
          <table className="w-full">
            <thead className="bg-zinc-900">
              <tr>
                <th className="px-4 py-3 text-left text-xs text-zinc-500">Data</th>
                <th className="px-4 py-3 text-left text-xs text-zinc-500">Nicho</th>
                <th className="px-4 py-3 text-left text-xs text-zinc-500">Vibe</th>
                <th className="px-4 py-3 text-left text-xs text-zinc-500">Status</th>
                <th className="px-4 py-3 text-left text-xs text-zinc-500">Score</th>
              </tr>
            </thead>
            <tbody>
              {generations.map((g) => (
                <tr key={g.id} className="border-t border-zinc-800 hover:bg-zinc-900/50">
                  <td className="px-4 py-3 text-sm">{new Date(g.created_at).toLocaleDateString("pt-BR")}</td>
                  <td className="px-4 py-3 text-sm">{g.niche}</td>
                  <td className="px-4 py-3 text-sm capitalize">{g.vibe}</td>
                  <td className="px-4 py-3"><StatusBadge status={g.status} /></td>
                  <td className="px-4 py-3 text-sm">{g.score ?? "-"}/10</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
