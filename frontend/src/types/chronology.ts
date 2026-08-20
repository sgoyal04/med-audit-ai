export interface ClinicalEvent {
  event_date: string;
  encounter_type: string;
  provider_or_facility: string | null;
  clinical_summary: string;
  medications: string[];
  source_page: number;
  source_quote: string;
}

export interface MasterChronology {
  patient_name: string | null;
  patient_dob: string | null;
  patient_age: string | null;
  events: ClinicalEvent[];
}

export interface SynthesisResponse {
  case_id: string;
  filename: string;
  total_pages: number;
  chronology: MasterChronology;
}