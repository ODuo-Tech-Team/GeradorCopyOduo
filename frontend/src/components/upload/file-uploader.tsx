"use client";
import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { Upload, FileText, Music } from "lucide-react";
import { cn } from "@/lib/utils";

interface Props {
  onUpload: (files: File[]) => void;
  isUploading: boolean;
}

export function FileUploader({ onUpload, isUploading }: Props) {
  const [error, setError] = useState<string | null>(null);

  const onDrop = useCallback((accepted: File[], rejected: unknown[]) => {
    setError(null);
    if ((rejected as unknown[]).length > 0) {
      setError("Arquivo inválido. Aceito: PDF, DOCX ou áudio (MP3, WAV, M4A)");
      return;
    }
    onUpload(accepted);
  }, [onUpload]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"], "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"], "audio/*": [".mp3", ".wav", ".m4a"] },
    multiple: true,
    maxSize: 50 * 1024 * 1024,
    disabled: isUploading,
  });

  return (
    <div
      {...getRootProps()}
      className={cn(
        "border-2 border-dashed rounded-xl p-6 md:p-12 text-center transition-all cursor-pointer",
        isDragActive && "border-blue-500 bg-blue-500/10",
        !isDragActive && "border-zinc-700 hover:border-zinc-600",
        isUploading && "opacity-50 cursor-not-allowed"
      )}
    >
      <input {...getInputProps()} />
      <div className="flex justify-center gap-3 md:gap-4 mb-3 md:mb-4">
        <FileText className="h-8 w-8 md:h-12 md:w-12 text-zinc-500" />
        <Music className="h-8 w-8 md:h-12 md:w-12 text-zinc-500" />
      </div>
      {isDragActive ? (
        <p className="text-base md:text-lg font-medium text-white">Solte os arquivos aqui...</p>
      ) : (
        <>
          <p className="text-base md:text-lg font-medium text-zinc-300 mb-2">Toque para selecionar ou arraste</p>
          <p className="text-xs md:text-sm text-zinc-500">PDF, DOCX, MP3, WAV, M4A (máx. 50MB cada)</p>
        </>
      )}
      {error && <p className="mt-4 text-sm text-red-500">{error}</p>}
    </div>
  );
}
