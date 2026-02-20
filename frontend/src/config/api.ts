export const API_CONFIG = {
  fastApiUrl: process.env.NEXT_PUBLIC_FASTAPI_URL || "http://localhost:8000",
  endpoints: {
    generate: "/api/v1/generate",
    briefingIdeas: "/api/v1/generate/briefing-ideas",
    history: "/api/v1/generate/history",
    stats: "/api/v1/generate/stats",
    generation: "/api/v1/generate",
    ingestPdf: "/api/v1/ingest/pdf",
    ingestDocx: "/api/v1/ingest/docx",
    ingestAudio: "/api/v1/ingest/audio",
    ingestAssets: "/api/v1/ingest/assets",
    health: "/api/v1/health",
  },
  timeouts: {
    upload: 60000,
    generation: 300000,
  },
} as const;
