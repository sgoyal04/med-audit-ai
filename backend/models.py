""" models.py: Core Pydantic schemas for MedAudit AI. """

from typing import List, Optional
from pydantic import BaseModel, Field

class PDFPageContent(BaseModel):
    """ Container for raw text extracted from a single PDF page. """
    
    page_number: int = Field(..., description="1-indexed human-readable page number.")
    raw_text: str = Field(..., description="Extracted plain text from the page.")
    character_count: int = Field(...,description="Totals character count on the page.")
    is_empty: bool = Field(default=False,description="True if no selectable text was found(potential scanned image).")
    
class ExtractedDocument(BaseModel):
    """ Container for the entire document's parsed page stream."""
    
    filename: str = Field(..., description="Original filename of the pdf.")
    total_pages: int = Field(...,description="Total page count in the document.")
    pages:List[PDFPageContent] = Field(default_factory=list, description="List of parsed pages.")
    
    def to_formatted_prompt_text(self) -> str:
        """Combines all pages into a structured prompt with explicit page boundary tags."""
        formatted_pages = []
        for page in self.pages:
            if not page.is_empty:
                formatted_pages.append(
                    f"=== START OF PAGE {page.page_number} ===\n"
                    f"{page.raw_text}\n"
                    f"=== END OF PAGE {page.page_number} ==="
                )
        return "\n\n".join(formatted_pages)
    
class ClinicalEvent(BaseModel):
    """ Schema representing a single clinical event extracted from medical notes. """
    
    event_date: str = Field(...,description="Standarized event data in ISO format YYYY-MM-DD or 'unknown")
    encounter_type: str = Field(...,description="Type of encounter, eg., 'Emergency', 'Surgery', 'Outpatient Follow-up', 'Lab Test'")
    provider_or_facility: Optional[str] = Field(default=None, description="Doctor name, clnic, hospital, or department responsible for the encounter.")
    clinical_summary: str = Field(..., description="Concise synthesis of patient complaints, vital signs, physical exam findings, or diagnosis.")
    medications: List[str] = Field(...,description="List of prescribed, administered, or discounted medications with dosages.")
    source_page: int = Field(...,description="1-indexed page number in the original PDF where this event was found.")
    source_quote: str = Field(...,description="Verbatim sentence from the source document supporting this event entry.")
    
class MasterChronology(BaseModel):
    """The master container holding the patient demographics and sorted timeline."""

    patient_name: Optional[str] = Field(default=None,description="Full legal name of the patient from headers or demographic blocks.")
    patient_dob: Optional[str] = Field(default=None,description="Patient Date of Birth, normalized strictly to ISO format YYYY-MM-DD.")
    patient_age: Optional[str] = Field(default=None,description="Patient age as an integer or string (e.g., '46').")
    events: List[ClinicalEvent] = Field(default_factory=list,description="All chronological medical events, past visits, and lab tests.")
        
class SynthesisResponse(BaseModel):
    case_id: str = Field(...,description="Unique uuid identifier for this clinical case.")
    filename: str = Field(...,description="Original filename of the document.")
    total_pages: int = Field(...,description="Total pages processed from the pdf.")
    chronology: MasterChronology = Field(...,description="The synthesized clinical chronology")