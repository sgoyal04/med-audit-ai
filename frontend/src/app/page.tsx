"use client";

import React, { useState } from "react";
import { SynthesisResponse } from "@/types/chronology";
import FileUpload from "@/components/FileUpload";
import ChronologyTable from "@/components/ChronologyTable";
import PdfViewer from "@/components/PdfViewer";
import { Activity, User, Calendar, RotateCcw } from "lucide-react";

export default function Home() {
  const [data, setData] = useState<SynthesisResponse | null>(null);
  const [activePage, setActivePage] = useState<number>(1);

  const handleReset = () => {
    setData(null);
    setActivePage(1);
  };

  return (
    <main className="h-screen flex flex-col bg-slate-100 text-slate-900 font-sans overflow-hidden">
      {/* Top Navbar */}
      <header className="h-14 bg-white border-b border-slate-200 px-6 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-2">
          <div className="p-1.5 bg-blue-600 rounded-lg text-white">
            <Activity className="w-5 h-5" />
          </div>
          <span className="font-bold text-slate-800 text-base tracking-tight">
            MedAudit <span className="text-blue-600">AI</span>
          </span>
        </div>

        {data && (
          <button
            onClick={handleReset}
            className="flex items-center gap-1.5 text-xs font-medium text-slate-600 hover:text-slate-900 bg-slate-100 hover:bg-slate-200 px-3 py-1.5 rounded-lg transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" /> Upload New Chart
          </button>
        )}
      </header>

      {/* Main Container */}
      {!data ? (
        <div className="flex-1 flex flex-col items-center justify-center p-6">
          <div className="text-center max-w-xl mb-6">
            <h1 className="text-3xl font-bold text-slate-900 tracking-tight">
              Clinical Document Intelligence
            </h1>
            <p className="text-slate-500 text-sm mt-2">
              Transform unstructured medical records into a synthesized, verifiable
              chronology with 1-click citation grounding.
            </p>
          </div>
          <FileUpload onSuccess={(result) => setData(result)} />
        </div>
      ) : (
        <div className="flex-1 flex flex-col overflow-hidden p-4 gap-4">
          {/* Patient Banner */}
          <div className="bg-white border border-slate-200 rounded-xl px-5 py-3 flex items-center justify-between shadow-sm flex-shrink-0">
            <div className="flex items-center gap-6 text-sm">
              <div className="flex items-center gap-2">
                <User className="w-4 h-4 text-slate-400" />
                <span className="text-slate-500">Patient:</span>
                <span className="font-semibold text-slate-800">
                  {data.chronology.patient_name || "Unknown"}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <Calendar className="w-4 h-4 text-slate-400" />
                <span className="text-slate-500">DOB:</span>
                <span className="font-medium text-slate-700">
                  {data.chronology.patient_dob || "N/A"}
                </span>
              </div>
              {data.chronology.patient_age && (
                <div>
                  <span className="text-slate-500">Age:</span>{" "}
                  <span className="font-medium text-slate-700">
                    {data.chronology.patient_age}
                  </span>
                </div>
              )}
            </div>

            <div className="text-xs text-slate-400 font-mono">
              {data.filename} ({data.total_pages} Pages)
            </div>
          </div>

          {/* Split-Screen Workspace */}
          <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-4 overflow-hidden">
            {/* Left: Master Chronology Table */}
            <div className="h-full flex flex-col bg-white border border-slate-200 rounded-xl p-4 overflow-hidden shadow-sm">
              <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100 flex-shrink-0">
                <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider">
                  Master Clinical Timeline ({data.chronology.events.length} Events)
                </h2>
                <span className="text-xs text-slate-400">Sorted Chronologically</span>
              </div>
              <div className="flex-1 overflow-hidden">
                <ChronologyTable
                  events={data.chronology.events}
                  activePage={activePage}
                  onPageSelect={(page) => setActivePage(page)}
                />
              </div>
            </div>

            {/* Right: Embedded Document Viewport */}
            <div className="h-full overflow-hidden">
              <PdfViewer caseId={data.case_id} currentPage={activePage} />
            </div>
          </div>
        </div>
      )}
    </main>
  );
}