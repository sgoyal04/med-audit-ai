"""
extractor.py: Document-level LLM Extraction Engine using Google GenAI SDK and .env configuration.
"""
import os, time, re
from typing import Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

from models import ExtractedDocument, MasterChronology

# Load environment variables from .env file
load_dotenv()

class LLMExtractionService:
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-3.6-flash"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is missing. Please add 'GEMINI_API_KEY=your_key' to your .env file."
            )

        self.client = genai.Client(api_key=self.api_key)
        self.model_name = model_name

    def extract_chronology(self, doc: ExtractedDocument, max_retries: int = 3) -> MasterChronology:
        """
        Extracts patient demographics, active doctor notes, past hospital visits, 
        and lab tests across the whole document.
        """
        formatted_document_text = doc.to_formatted_prompt_text()

        if not formatted_document_text.strip():
            return MasterChronology(patient_name="Unknown", events=[])

        system_instruction = (
            "You are a clinical document intelligence engine. Your goal is to synthesize a structured medical history from multi-page charts."

            "EXTRACTION GUIDELINES:"
            "1. Demographics: Prioritize official intake headers or demographics sections for patient name and DOB. Normalize all dates to YYYY-MM-DD."
            "2. Clinical Chronology: "
                "- Parse active doctor notes (SOAP notes, assessments, plans)."
                "- Parse all tabular data (e.g., 'Past Hospital Visits', 'Medical Tests') as distinct individual events."
            "3. Verification Anchors: Every event must include the exact 1-indexed `source_page` and a verbatim `source_quote`."
            "4. Strict Grounding: Do not infer or hallucinate clinical facts not directly supported by the text."
        )

        user_prompt = f"PATIENT MEDICAL DOCUMENT:\n\n{formatted_document_text}"

        last_error = None
        for attempt in range(1, max_retries + 1):
            try:
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        response_mime_type="application/json",
                        response_schema=MasterChronology,
                        temperature=0.0,
                    ),
                )

                master_chronology: Optional[MasterChronology] = None

                # Primary: Attempt to use SDK's parsed property
                if hasattr(response, "parsed") and isinstance(response.parsed, MasterChronology):
                    master_chronology = response.parsed
                elif hasattr(response, "parsed") and isinstance(response.parsed, dict):
                    master_chronology = MasterChronology.model_validate(response.parsed)

                # Fallback: Parse raw response text if parsed was None
                if master_chronology is None and response.text:
                    raw_text = response.text.strip()
                    # Strip markdown code blocks if present (```json ... ```)
                    cleaned_json = re.sub(r"^```(?:json)?\s*", "", raw_text, flags=re.IGNORECASE)
                    cleaned_json = re.sub(r"\s*```$", "", cleaned_json.strip())
                    master_chronology = MasterChronology.model_validate_json(cleaned_json)

                if master_chronology is None:
                    raise ValueError("Failed to obtain a valid MasterChronology schema from the model response.")

                # Sort events deterministically (earliest to latest)
                def sort_key(event):
                    return "9999-99-99" if event.event_date == "Unknown" else event.event_date

                master_chronology.events.sort(key=sort_key)
                return master_chronology

            except Exception as e:
                last_error = e
                error_str = str(e)
                if "503" in error_str or "UNAVAILABLE" in error_str:
                    if attempt < max_retries:
                        wait_time = attempt * 2
                        print(f"[!] 503 High Demand received. Retrying in {wait_time}s (Attempt {attempt}/{max_retries})...")
                        time.sleep(wait_time)
                        continue
                raise e

        # If retries exhausted
        raise RuntimeError(f"Extraction failed after {max_retries} attempts: {last_error}")