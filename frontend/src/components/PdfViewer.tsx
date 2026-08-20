"use client";

import React from "react";
import { FileText, ExternalLink } from "lucide-react";

interface PdfViewerProps {
  caseId: string;
  currentPage: number;
}

export default function PdfViewer({ caseId, currentPage }: PdfViewerProps) {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  // The #page=X hash tells the browser's PDF engine which page to display
  const pdfUrl = `${apiUrl}/api/documents/${caseId}#page=${currentPage}&toolbar=1&navpanes=0`;

  return (
    <div className="h-full flex flex-col bg-slate-900 rounded-xl overflow-hidden border border-slate-800 shadow-sm">
      {/* Header Bar */}
      <div className="px-4 py-2.5 bg-slate-800/90 border-b border-slate-700 flex items-center justify-between text-xs text-slate-300 flex-shrink-0">
        <span className="flex items-center gap-2 font-medium">
          <FileText className="w-4 h-4 text-blue-400" /> Grounded Source Viewport
        </span>
        <div className="flex items-center gap-2">
          <span className="bg-blue-900/60 text-blue-300 border border-blue-700/50 px-2.5 py-0.5 rounded font-mono font-semibold">
            Active Page: {currentPage}
          </span>
          <a
            href={pdfUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="p-1 hover:bg-slate-700 rounded text-slate-400 hover:text-slate-200 transition-colors"
            title="Open in new tab"
          >
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>

      {/* PDF Viewport */}
      <div className="flex-1 w-full h-full bg-slate-800 relative">
        <object
          key={`${caseId}-page-${currentPage}`}
          data={pdfUrl}
          type="application/pdf"
          className="w-full h-full"
        >
          <div className="flex flex-col items-center justify-center h-full text-slate-400 text-sm gap-2 p-6 text-center">
            <p>Unable to display PDF directly in your browser.</p>
            <a
              href={pdfUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 hover:underline flex items-center gap-1"
            >
              Open PDF in a new tab <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
        </object>
      </div>
    </div>
  );
}