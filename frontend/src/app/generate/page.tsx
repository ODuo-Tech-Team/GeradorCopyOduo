import { GenerationForm } from "@/components/generator/generation-form";

export default function GeneratePage() {
  return (
    <div className="space-y-8">
      <div className="max-w-3xl mx-auto text-center">
        <h1 className="text-4xl font-bold text-white mb-3">Gerar Carrossel</h1>
        <p className="text-zinc-400">
          Selecione o nicho, tom e escreva o briefing para gerar 3 opções de carrossel com 7 slides cada
        </p>
      </div>
      <GenerationForm />
    </div>
  );
}
