""" 
main.py: FastAPI Backend Service for MedAudit AI.
Handles PDF uploads, LLM extraction orchestration, caching, and document serving.
"""

import os, uuid
from pathlib import Path
from typing import Dict, Any, List

import traceback
from fastapi.responses import JSONResponse
from fastapi import FastAPI, File, UploadFile, HTTPException, status, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from models import MasterChronology, ExtractedDocument, SynthesisResponse, CaseSummaryResponse
from parser import PDFParserService
from extractor import LLMExtractionService
from database import get_case_by_id, list_all_cases, init_db, save_case, get_db


init_db()

# 1. Initialize Application
app = FastAPI(
    title="MedAudit AI Engine",
    description="Intelligence Clinical Document Ingestion and Chronology Synthesizer",
    version="1.0.0",
)

# 2. Define allowed origins (frontend urls)
origins = [
    "http://localhost:3000",          # Local React/Next.js dev server
    "http://127.0.0.1:5500",          # Live Server / HTML frontend
    "https://your-frontend-domain.com" # Production frontend
]

# 3. Configure CORS (Cross-Origin Resource Sharing)
# Allows React / Next.js frontend 
app.add_middleware(
    CORSMiddleware,
        allow_origins=origins,            # Or ["*"] to allow all origins (dev only)
        allow_credentials=True,           # Allow cookies / Authorization headers
        allow_methods=["*"],              # Allowed HTTP methods (GET, POST, PUT, DELETE, etc.)
        allow_headers=["*"],              # Allowed request headers
)

# 4. Directories and In-Memory Database
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# # In memory store for demo/development purposes
# CHRONOLOGY_DB: Dict[str, Dict[str, Any]] = {}

# Initialize the LLM Extraction Service
extractor_service = LLMExtractionService()

# -----------------------------------
# API Endpoints
# -----------------------------------

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
  """Catches any unhandled 500 error and returns the exact Python traceback in development."""
  return JSONResponse(
      status_code=500,
      content={
          "error_type": type(exc).__name__,
          "detail": str(exc),
          "traceback": traceback.format_exc().splitlines(),
      },
  )
  
from fastapi.exceptions import ResponseValidationError


@app.exception_handler(ResponseValidationError)
async def response_validation_exception_handler(
    request: Request, exc: ResponseValidationError
):
  return JSONResponse(
      status_code=500,
      content={
          "error_type": "ResponseValidationError",
          "errors": exc.errors(),  # This tells you the exact offending field!
      },
  )

@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoints to verify backend status."""
    return {
        "status":"healthy",
        "service": "MedAudit AI",
        "engine": "gemini-3.6-flash",
    }
    
@app.post(
    "/api/chronology/synthesize",
    response_model = SynthesisResponse,
    status_code = status.HTTP_201_CREATED,
    tags=["Synthesis"],
)
async def synthesize_medical_chronology(file:UploadFile = File(...), db: Session = Depends(get_db)):
    """
        Uploads a clinical PDF, extracts text page-by-page, and returns
        a fully synthesized, gronded medical chronology.
    """
    # Validate file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PDF documents(.pdf) are supported.",
        )
    try:
        # Read bytes into memory
        file_bytes = await file.read()
        if len(file_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded PDF file is empty.",
            )
            
        # Parse PDF into pages using PyMuPDF service
        doc: ExtractedDocument = PDFParserService.extract_from_bytes(
            file_bytes=file_bytes, filename=file.filename
        )
        
        # Run LLM semantic Extraction Engine
        chronology: MasterChronology = extractor_service.extract_chronology(doc)
        
        # Persist PDF to disk so that frontend can display it in viewport
        case_id = str(uuid.uuid4())
        saved_file_path = UPLOAD_DIR / f"{case_id}.pdf"
        with open(saved_file_path, "wb") as f:
            f.write(file_bytes)
            
        # Store in state dictionary
        record = save_case(
            case_id=case_id,
            filename=file.filename,
            total_pages=doc.total_pages,
            file_path=str(saved_file_path),
            patient_name=chronology.patient_name,
            patient_dob=chronology.patient_dob,
            patient_age=chronology.patient_age,
            chronology_dict=chronology.model_dump(), 
            db=db
        )
        return record
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing the chart: {str(e)}",
        )
        
@app.get(
    "/api/chronology/{case_id}",
    response_model=SynthesisResponse,
    tags=["Synthesis"],
)
async def get_chronology_by_id(case_id: str, db: Session = Depends(get_db)):
    """Retrieves an existing synthesized clinical chronology by its unique case_id."""
    record = get_case_by_id(case_id,db)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No record found for Case Id: {case_id}",
        )
    return record

@app.get(
    "/api/cases",
    response_model=List[CaseSummaryResponse],
    tags=["Dashboard"]
)
async def get_cases(db:Session = Depends(get_db)):
    return list_all_cases(db)
    
    
@app.get(
    "/api/documents/{case_id}",
    tags=["Documents"]
)
async def stream_document_pdf(case_id: str, db: Session = Depends(get_db)):
    """Streams the raw PDF file to the frontend embedded PDF viewer."""
    record = get_case_by_id(case_id, db)
    # Use record.file_path (attribute access), not record["file_path"]
    if not record or not os.path.exists(record.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF document not found for this case"
        )
    return FileResponse(
        path=record.file_path,
        media_type="application/pdf",
        content_disposition_type="inline",
    )

