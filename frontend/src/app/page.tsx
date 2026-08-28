"use client";

import React, { useState } from "react";
import { SynthesisResponse } from "@/types/chronology";
import FileUpload from "@/components/FileUpload";
import ChronologyTable from "@/components/ChronologyTable";
import PdfViewer from "@/components/PdfViewer";
import CaseDashboard from "@/components/CaseDashboard";
import { Activity, User, Calendar } from "lucide-react";

export default function Home() {
  const [data, setData] = useState<SynthesisResponse | null>(null);
  const [activePage, setActivePage] = useState<number>(1);
  const [isUploadingNew, setIsUploadingNew] = useState<boolean>(false);

  const handleSelectCase = async (caseId: string) => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${apiUrl}/api/chronology/${caseId}`);
      if (res.ok) {
        const caseData: SynthesisResponse = await res.json();
        setData(caseData);
        setActivePage(1);
        setIsUploadingNew(false);
      }
    } catch (err) {
      console.error("Failed to load case data:", err);
    }
  };

  const handleNewUpload = () => {
    setData(null);
    setIsUploadingNew(true);
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
      </header>

      {/* Main Workspace Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Persistent Case History Sidebar */}
        <CaseDashboard
          selectedCaseId={data?.case_id || null}
          onSelectCase={handleSelectCase}
          onNewUpload={handleNewUpload}
        />

        {/* Content Area */}
        <section className="flex-1 flex flex-col overflow-hidden p-4">
          {!data || isUploadingNew ? (
            <div className="flex-1 flex flex-col items-center justify-center p-6 bg-white rounded-xl border border-slate-200 shadow-sm">
              <div className="text-center max-w-xl mb-6">
                <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
                  New Medical Record Audit
                </h1>
                <p className="text-slate-500 text-xs mt-1">
                  Upload patient chart PDF to extract clinical events and persist them in your database.
                </p>
              </div>
              <FileUpload
                onSuccess={(result) => {
                  setData(result);
                  setIsUploadingNew(false);
                }}
              />
            </div>
          ) : (
            <div className="flex-1 flex flex-col overflow-hidden gap-4">
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
                <div className="h-full flex flex-col bg-white border border-slate-200 rounded-xl p-4 overflow-hidden shadow-sm">
                  <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100 flex-shrink-0">
                    <h2 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
                      Master Clinical Timeline ({data.chronology.events.length} Events)
                    </h2>
                    <span className="text-[11px] text-slate-400">Sorted Chronologically</span>
                  </div>
                  <div className="flex-1 overflow-hidden">
                    <ChronologyTable
                      events={data.chronology.events}
                      activePage={activePage}
                      onPageSelect={(page) => setActivePage(page)}
                    />
                  </div>
                </div>

                <div className="h-full overflow-hidden">
                  <PdfViewer caseId={data.case_id} currentPage={activePage} />
                </div>
              </div>
            </div>
          )}
        </section>
      </div>
    </main>
  );
}