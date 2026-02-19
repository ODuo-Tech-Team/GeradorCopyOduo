import { Card } from "@/components/ui/card";

interface Props {
  title: string;
  value: string | number;
  description?: string;
}

export function StatsCard({ title, value, description }: Props) {
  return (
    <Card className="p-6 bg-zinc-900 border-zinc-800">
      <p className="text-sm text-zinc-500">{title}</p>
      <p className="text-3xl font-bold text-white mt-1">{value}</p>
      {description && <p className="text-xs text-zinc-500 mt-1">{description}</p>}
    </Card>
  );
}
