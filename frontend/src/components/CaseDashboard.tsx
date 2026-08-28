"use client";

import React, { useEffect, useState } from "react";
import { CaseSummary } from "@/types/chronology";
import { FolderGit2, User, Clock, FileText, ChevronRight, PlusCircle } from "lucide-react";

interface CaseDashboardProps {
  selectedCaseId: string | null;
  onSelectCase: (caseId: string) => void;
  onNewUpload: () => void;
}

export default function CaseDashboard({
  selectedCaseId,
  onSelectCase,
  onNewUpload,
}: CaseDashboardProps) {
  const [cases, setCases] = useState<CaseSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchCases = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/cases`);
      if (res.ok) {
        const data = await res.json();
        setCases(data);
      }
    } catch (err) {
      console.error("Failed to load historical cases:", err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, [selectedCaseId]);

  return (
    <aside className="w-80 h-full bg-white border-r border-slate-200 flex flex-col shrink-0">
      {/* Header & New Audit CTA */}
      <div className="p-4 border-b border-slate-100 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FolderGit2 className="w-4 h-4 text-blue-600" />
          <h3 className="font-bold text-slate-800 text-sm tracking-tight">Active Audit Cases</h3>
        </div>
        <button
          onClick={onNewUpload}
          className="flex items-center gap-1 text-xs font-semibold bg-blue-50 hover:bg-blue-100 text-blue-700 px-2.5 py-1.5 rounded-lg transition-colors"
        >
          <PlusCircle className="w-3.5 h-3.5" /> New Case
        </button>
      </div>

      {/* Case List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {isLoading ? (
          <div className="text-xs text-slate-400 p-4 text-center">Loading audit history...</div>
        ) : cases.length === 0 ? (
          <div className="text-xs text-slate-400 p-6 text-center">
            No historical cases found. Upload a medical chart to start.
          </div>
        ) : (
          cases.map((c) => {
            const isSelected = selectedCaseId === c.case_id;
            return (
              <button
                key={c.case_id}
                onClick={() => onSelectCase(c.case_id)}
                className={`w-full text-left p-3 rounded-xl border transition-all duration-150 ${
                  isSelected
                    ? "bg-blue-50/80 border-blue-400 shadow-sm ring-1 ring-blue-400"
                    : "bg-white border-slate-200 hover:border-slate-300 hover:bg-slate-50/50"
                }`}
              >
                <div className="flex items-center justify-between gap-1 mb-1">
                  <span className="font-semibold text-xs text-slate-800 truncate flex items-center gap-1.5">
                    <User className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                    {c.patient_name}
                  </span>
                  <ChevronRight className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                </div>

                <div className="text-[11px] text-slate-500 flex items-center gap-1 truncate mb-2">
                  <FileText className="w-3 h-3 text-slate-400" /> {c.filename}
                </div>

                <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1 border-t border-slate-100">
                  <span className="bg-slate-100 text-slate-600 px-1.5 py-0.5 rounded font-mono">
                    {c.event_count} events
                  </span>
                  <span className="flex items-center gap-1 font-mono">
                    <Clock className="w-2.5 h-2.5" /> {c.created_at}
                  </span>
                </div>
              </button>
            );
          })
        )}
      </div>
    </aside>
  );
}