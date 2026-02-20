"use client";
import { useEffect, useState } from "react";
import { StatsCard } from "@/components/dashboard/stats-card";
import { Sparkles, Upload } from "lucide-react";
import { apiRequest } from "@/lib/api/client";
import { API_CONFIG } from "@/config/api";
import Link from "next/link";

interface DashboardStats {
  total_generations: number;
  total_assets: number;
  total_winners: number;
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);

  useEffect(() => {
    apiRequest<DashboardStats>(API_CONFIG.endpoints.stats)
      .then(setStats)
      .catch((err) => console.error("Erro ao buscar stats:", err));
  }, []);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl md:text-4xl font-bold text-white">Dashboard</h1>
        <p className="text-zinc-500 mt-1 text-sm md:text-base">Visão geral do seu gerador de copys</p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-3 md:gap-6">
        <StatsCard title="Gerações" value={stats?.total_generations ?? 0} description="Total de carrosséis gerados" />
        <StatsCard title="Assets" value={stats?.total_assets ?? 0} description="PDFs e áudios carregados" />
        <StatsCard title="Vencedoras" value={stats?.total_winners ?? 0} description="Copys marcadas como top" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 md:gap-6">
        <Link href="/generate" className="block">
          <div className="border border-zinc-800 rounded-xl p-5 md:p-8 hover:border-blue-500 transition-colors group">
            <Sparkles className="h-6 w-6 md:h-8 md:w-8 text-blue-500 mb-3 md:mb-4" />
            <h2 className="text-lg md:text-xl font-bold text-white group-hover:text-blue-400 transition-colors">Gerar Copy</h2>
            <p className="text-zinc-500 mt-1 md:mt-2 text-sm">Crie 3 opções de carrossel com 7 slides cada</p>
          </div>
        </Link>
        <Link href="/upload" className="block">
          <div className="border border-zinc-800 rounded-xl p-5 md:p-8 hover:border-green-500 transition-colors group">
            <Upload className="h-6 w-6 md:h-8 md:w-8 text-green-500 mb-3 md:mb-4" />
            <h2 className="text-lg md:text-xl font-bold text-white group-hover:text-green-400 transition-colors">Upload de Material</h2>
            <p className="text-zinc-500 mt-1 md:mt-2 text-sm">Suba PDFs e áudios para enriquecer as copys com RAG</p>
          </div>
        </Link>
      </div>
    </div>
  );
}
