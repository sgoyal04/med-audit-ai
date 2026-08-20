"use client";

import React, { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";
import { UploadCloud, FileText, Loader2, AlertCircle } from "lucide-react";
import { SynthesisResponse } from "@/types/chronology";

interface FileUploadProps {
  onSuccess: (data: SynthesisResponse) => void;
}

export default function FileUpload({ onSuccess }: FileUploadProps) {
  const [isProcessing, setIsProcessing] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

const onDrop = useCallback(
  async (acceptedFiles: File[]) => {
    // 1. Guard against re-entrancy / double triggers
    if (isProcessing) return;

    const file = acceptedFiles[0];
    if (!file) return;

    setIsProcessing(true);
    setErrorMessage(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/api/chronology/synthesize`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to process the document.");
      }

      const data: SynthesisResponse = await response.json();
      onSuccess(data);
    } catch (err: any) {
      setErrorMessage(err.message || "An unexpected error occurred.");
    } finally {
      setIsProcessing(false);
    }
  },
  [isProcessing, onSuccess]
);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"] },
    multiple: false,
    disabled: isProcessing,
  });

  return (
    <div className="w-full max-w-2xl mx-auto p-6">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-2xl p-10 flex flex-col items-center justify-center text-center cursor-pointer transition-all duration-200 ${
          isDragActive
            ? "border-blue-500 bg-blue-50/50"
            : "border-slate-300 hover:border-blue-400 bg-white"
        } ${isProcessing ? "opacity-60 cursor-not-allowed" : ""}`}
      >
        <input {...getInputProps()} />

        {isProcessing ? (
          <div className="flex flex-col items-center gap-3">
            <Loader2 className="w-12 h-12 text-blue-600 animate-spin" />
            <p className="font-semibold text-slate-800 text-lg">
              Synthesizing Clinical Chronology...
            </p>
            <p className="text-sm text-slate-500">
              Extracting pages, grounding citations, and sorting clinical events.
            </p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-3">
            <div className="p-4 bg-blue-50 rounded-full text-blue-600">
              <UploadCloud className="w-8 h-8" />
            </div>
            <div>
              <p className="font-semibold text-slate-800 text-base">
                Drop your medical chart PDF here, or{" "}
                <span className="text-blue-600 underline">browse</span>
              </p>
              <p className="text-xs text-slate-400 mt-1">
                Supports clinical intake summaries, SOAP notes, and lab reports
              </p>
            </div>
          </div>
        )}
      </div>

      {errorMessage && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-xl flex items-center gap-3 text-red-700 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}
    </div>
  );
}