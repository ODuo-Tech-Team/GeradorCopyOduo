export const VIBES = [
  { value: "educativo", label: "Educativo", description: "Tom didático e informativo", icon: "GraduationCap" },
  { value: "urgente", label: "Urgente", description: "Senso de urgência e escassez", icon: "Zap" },
  { value: "autoridade", label: "Autoridade", description: "Tom de especialista confiável", icon: "Shield" },
  { value: "provocativo", label: "Provocativo", description: "Desafia crenças e provoca reflexão", icon: "Flame" },
] as const;

export const SLIDE_TYPES: Record<string, { label: string; color: string }> = {
  hook: { label: "Hook", color: "bg-purple-500" },
  dor: { label: "Dor", color: "bg-red-500" },
  solucao: { label: "Solução", color: "bg-green-500" },
  prova: { label: "Prova", color: "bg-yellow-500" },
  beneficio: { label: "Benefício", color: "bg-indigo-500" },
  objecao: { label: "Objeção", color: "bg-orange-500" },
  cta: { label: "CTA", color: "bg-pink-500" },
};

export const NICHES = [
  { value: "construcao-civil", label: "Construção Civil" },
  { value: "veiculos", label: "Veículos" },
  { value: "tecnologia", label: "Tecnologia" },
  { value: "eventos", label: "Eventos" },
  { value: "imoveis-residenciais", label: "Imóveis Residenciais" },
  { value: "imoveis-comerciais", label: "Imóveis Comerciais" },
  { value: "equipamentos-industriais", label: "Equipamentos Industriais" },
  { value: "ferramentas", label: "Ferramentas" },
  { value: "jardinagem", label: "Jardinagem" },
  { value: "esportes-lazer", label: "Esportes e Lazer" },
] as const;

export const MAX_FILE_SIZE = 50 * 1024 * 1024;
export const ACCEPTED_FILE_TYPES = {
  pdf: ["application/pdf"],
  audio: ["audio/mpeg", "audio/wav", "audio/mp3", "audio/m4a"],
};
