"use client";
import { useState, useEffect } from "react";
import { FileUploader } from "@/components/upload/file-uploader";
import { StatusBadge } from "@/components/shared/status-badge";
import { API_CONFIG } from "@/config/api";

interface UploadedFile {
  name: string;
  status: string;
  chunks: number;
}

export default function UploadPage() {
  const [uploading, setUploading] = useState(false);
  const [sessionUploads, setSessionUploads] = useState<UploadedFile[]>([]);
  const [savedAssets, setSavedAssets] = useState<UploadedFile[]>([]);

  useEffect(() => {
    async function loadAssets() {
      try {
        const resp = await fetch(`${API_CONFIG.fastApiUrl}${API_CONFIG.endpoints.ingestAssets}`);
        if (resp.ok) {
          const data = await resp.json();
          setSavedAssets(
            data.map((a: { file_name: string; processing_status: string; chunks_count: number }) => ({
              name: a.file_name,
              status: a.processing_status,
              chunks: a.chunks_count || 0,
            }))
          );
        }
      } catch {
        // silently fail - assets will show from session only
      }
    }
    loadAssets();
  }, []);

  const handleUpload = async (files: File[]) => {
    setUploading(true);

    for (const file of files) {
      try {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("niche", "geral");

        const isDocx = file.name.endsWith(".docx") || file.name.endsWith(".doc");
        const isPdf = file.name.endsWith(".pdf");
        const endpoint = isDocx ? API_CONFIG.endpoints.ingestDocx : isPdf ? API_CONFIG.endpoints.ingestPdf : API_CONFIG.endpoints.ingestAudio;

        const response = await fetch(`${API_CONFIG.fastApiUrl}${endpoint}`, {
          method: "POST",
          body: formData,
        });
        const data = await response.json();

        setSessionUploads((prev) => [
          { name: file.name, status: data.success ? "completed" : "failed", chunks: data.chunks_created || 0 },
          ...prev,
        ]);
      } catch {
        setSessionUploads((prev) => [{ name: file.name, status: "failed", chunks: 0 }, ...prev]);
      }
    }
    setUploading(false);
  };

  // Combina uploads da sessao com historico, removendo duplicatas
  const allUploads = [
    ...sessionUploads,
    ...savedAssets.filter((a) => !sessionUploads.some((s) => s.name === a.name)),
  ];

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl md:text-4xl font-bold text-white">Upload de Material</h1>
        <p className="text-zinc-500 mt-1 text-sm md:text-base">Suba documentos de referência para a IA usar como base nas copys</p>
      </div>

      <div className="max-w-2xl">
        <FileUploader onUpload={handleUpload} isUploading={uploading} />
      </div>

      {allUploads.length > 0 && (
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-white">Uploads Recentes</h2>
          {allUploads.map((u, i) => (
            <div key={i} className="flex items-center justify-between border border-zinc-800 rounded-lg p-4">
              <div>
                <p className="text-white font-medium">{u.name}</p>
                <p className="text-xs text-zinc-500">{u.chunks} chunks processados</p>
              </div>
              <StatusBadge status={u.status} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
