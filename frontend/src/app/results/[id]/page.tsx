import ResultsClient from "./results-client";

export async function generateStaticParams() {
  return [{ id: "latest" }];
}

export const dynamicParams = false;

export default function ResultsPage({ params }: { params: Promise<{ id: string }> }) {
  return <ResultsClient params={params} />;
}
