"""
run_real_pdf.py: Test extraction on your clinical PDF using .env credentials.
"""
import os
from dotenv import load_dotenv
from parser import PDFParserService
from extractor import LLMExtractionService

# Load .env variables
load_dotenv()
INPUT_PATH = "input/Easy"

def main():
    pdf_filename = "PDF_Deid_Deidentification_0.pdf"
    
    # Combine the folder and the filename
    pdf_filename = os.path.join(INPUT_PATH, pdf_filename)

    if not os.path.exists(pdf_filename):
        print(f"[!] Please place '{pdf_filename}' in the root directory.")
        return

    print(f"[*] Step 1: Parsing '{pdf_filename}' with PyMuPDF...")
    doc = PDFParserService.extract_from_path(pdf_filename)
    print(f"[✓] Successfully parsed {doc.total_pages} pages.\n")

    print("[*] Step 2: Extracting clinical timeline using Gemini 2.5 Flash...")
    try:
        extractor = LLMExtractionService()
        chronology = extractor.extract_chronology(doc)
    except Exception as e:
        print(f"[!] Error during extraction: {e}")
        return

    print("\n" + "=" * 80)
    print("                    MASTER CLINICAL CHRONOLOGY")
    print("=" * 80)
    print(f"Patient Name : {chronology.patient_name}")
    print(f"DOB          : {chronology.patient_dob} (Age: {chronology.patient_age})")
    print(f"Total Events : {len(chronology.events)}")
    print("=" * 80 + "\n")

    for i, event in enumerate(chronology.events, start=1):
        print(f"[{i:02d}] {event.event_date} | {event.encounter_type}")
        print(f"     Provider : {event.provider_or_facility}")
        print(f"     Summary  : {event.clinical_summary}")
        if event.medications:
            print(f"     Meds     : {', '.join(event.medications)}")
        print(f"     Citation : Page {event.source_page} -> \"{event.source_quote}\"")
        print("-" * 80)


if __name__ == "__main__":
    main()