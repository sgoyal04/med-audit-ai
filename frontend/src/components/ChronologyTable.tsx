"use client";

import React from "react";
import { ClinicalEvent } from "@/types/chronology";
import { Calendar, User, Pill, ExternalLink } from "lucide-react";

interface ChronologyTableProps {
  events: ClinicalEvent[];
  activePage: number;
  onPageSelect: (pageNumber: number) => void;
}

export default function ChronologyTable({
  events,
  activePage,
  onPageSelect,
}: ChronologyTableProps) {
  return (
    <div className="overflow-y-auto h-full pr-2 space-y-3">
      {events.map((event, idx) => {
        const isSelected = activePage === event.source_page;
        return (
          <div
            key={idx}
            className={`p-4 rounded-xl border transition-all duration-150 ${
              isSelected
                ? "bg-blue-50/70 border-blue-400 shadow-sm ring-1 ring-blue-400"
                : "bg-white border-slate-200 hover:border-slate-300"
            }`}
          >
            {/* Header: Date + Encounter Type + Page Badge */}
            <div className="flex items-center justify-between gap-2 mb-2">
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-100 text-slate-700">
                  <Calendar className="w-3.5 h-3.5 text-slate-500" />
                  {event.event_date}
                </span>
                <span className="px-2 py-0.5 rounded text-xs font-medium bg-blue-100/70 text-blue-700">
                  {event.encounter_type}
                </span>
              </div>

              {/* Interactive Page Badge */}
              <button
                onClick={() => onPageSelect(event.source_page)}
                className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-md text-xs font-medium transition-colors ${
                  isSelected
                    ? "bg-blue-600 text-white"
                    : "bg-slate-100 hover:bg-blue-50 text-slate-600 hover:text-blue-600"
                }`}
                title="Jump to this page in document"
              >
                Page {event.source_page}
                <ExternalLink className="w-3 h-3" />
              </button>
            </div>

            {/* Provider */}
            {event.provider_or_facility && (
              <p className="text-xs text-slate-500 flex items-center gap-1 mb-2">
                <User className="w-3 h-3" /> {event.provider_or_facility}
              </p>
            )}

            {/* Clinical Summary */}
            <p className="text-sm text-slate-800 leading-relaxed mb-2 font-normal">
              {event.clinical_summary}
            </p>

            {/* Medications */}
            {event.medications && event.medications.length > 0 && (
              <div className="flex flex-wrap items-center gap-1.5 mb-3">
                <Pill className="w-3.5 h-3.5 text-emerald-600" />
                {event.medications.map((med, medIdx) => (
                  <span
                    key={medIdx}
                    className="px-2 py-0.5 text-xs bg-emerald-50 text-emerald-700 border border-emerald-200/60 rounded"
                  >
                    {med}
                  </span>
                ))}
              </div>
            )}

            {/* Grounding Source Quote */}
            <div className="bg-slate-50 p-2 rounded-lg border-l-2 border-slate-300 text-xs text-slate-500 italic">
              &ldquo;{event.source_quote}&rdquo;
            </div>
          </div>
        );
      })}
    </div>
  );
}