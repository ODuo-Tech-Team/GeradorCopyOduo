import { StatsCard } from "@/components/dashboard/stats-card";
import { Sparkles, Upload } from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-4xl font-bold text-white">Dashboard</h1>
        <p className="text-zinc-500 mt-1">Visão geral do seu gerador de copys</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatsCard title="Gerações" value={0} description="Total de carrosséis gerados" />
        <StatsCard title="Assets" value={0} description="PDFs e áudios carregados" />
        <StatsCard title="Vencedoras" value={0} description="Copys marcadas como top" />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Link href="/generate" className="block">
          <div className="border border-zinc-800 rounded-xl p-8 hover:border-blue-500 transition-colors group">
            <Sparkles className="h-8 w-8 text-blue-500 mb-4" />
            <h2 className="text-xl font-bold text-white group-hover:text-blue-400 transition-colors">Gerar Copy</h2>
            <p className="text-zinc-500 mt-2">Crie 3 opções de carrossel com 7 slides cada</p>
          </div>
        </Link>
        <Link href="/upload" className="block">
          <div className="border border-zinc-800 rounded-xl p-8 hover:border-green-500 transition-colors group">
            <Upload className="h-8 w-8 text-green-500 mb-4" />
            <h2 className="text-xl font-bold text-white group-hover:text-green-400 transition-colors">Upload de Material</h2>
            <p className="text-zinc-500 mt-2">Suba PDFs e áudios para enriquecer as copys com RAG</p>
          </div>
        </Link>
      </div>
    </div>
  );
}
