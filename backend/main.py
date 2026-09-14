""" 
main.py: FastAPI Backend Service for MedAudit AI.
"""

from __future__ import annotations
import os, uuid
from pathlib import Path
from typing import Annotated, List

import traceback
from fastapi.responses import JSONResponse
from fastapi.exceptions import ResponseValidationError
from fastapi import FastAPI, File, UploadFile, HTTPException, status, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from models import MasterChronology, ExtractedDocument
from schemas import SynthesisResponse, CaseSummaryResponse, UserCreate, UserResponse,UserUpdate
from parser import PDFParserService
from extractor import LLMExtractionService
import database

from contextlib import asynccontextmanager

database.init_db()

# 1. Initialize Application
app = FastAPI(
    title="MedAudit AI Engine",
    description="Intelligence Clinical Document Ingestion and Chronology Synthesizer",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/media", StaticFiles(directory="media"), name="media")

# 2. Define allowed origins (frontend urls)
origins = [
    "http://localhost:3000",          # Local React/Next.js dev server
    "http://127.0.0.1:5500",          # Live Server / HTML frontend
    "https://frontend-domain.com" # Production frontend
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

# Dependancy injections
type db_dependancy = Annotated[Session, Depends(database.get_db)]

def get_existing_user(user_id:str, db: db_dependancy):
    "Fetches user by user id"
    user = database.get_user_by_id(user_id=user_id,db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    return user

def validate_user_details(user:UserCreate, db:db_dependancy) -> UserCreate:
    if user.username is None or user.email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and email can not be none/empty string"
        )
    existing_user = database.get_user_by_name(user.username,db)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists."
        )
        
    existing_email = database.get_user_by_email(user.email,db)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There is an account associated with this email."
        )
    return user
    

type user_dependancy = Annotated[database.User, Depends(get_existing_user)]
type validate_user_dependancy = Annotated[UserCreate, Depends(validate_user_details)]    

# -----------------------------------
# API Endpoints
# -----------------------------------

@app.exception_handler(Exception)
def global_exception_handler(request: Request, exc: Exception):
  """Catches any unhandled 500 error and returns the exact Python traceback in development."""
  return JSONResponse(
      status_code=500,
      content={
          "error_type": type(exc).__name__,
          "detail": str(exc),
          "traceback": traceback.format_exc().splitlines(),
      },
  )
  

@app.exception_handler(ResponseValidationError)
def response_validation_exception_handler(
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
def health_check():
    """Health check endpoints to verify backend status."""
    return {
        "status":"healthy",
        "service": "MedAudit AI",
        "engine": "gemini-3.6-flash",
    }
    
# TODO: validate email    
@app.post(
    "/api/user",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["User"]
)
def create_user(user:validate_user_dependancy, db: db_dependancy):
    """
        Creates a new user account if it does not exist already.
    """
    
    # ensure_valid_user_details(user_email=user.email,username=user.username,db=db)
        
    try:
        user_id = str(uuid.uuid4())
        user = database.create_new_user(user_id=user_id,username=user.username,user_email=user.email,db=db)
        return user

    except HTTPException:
            raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while creating a new user: {str(e)}",
        )
        
# TODO: Validate email
# Verification handled by user dependancy
@app.patch(
    "/api/users/{user_id}",
    response_model=UserResponse,
    tags=["User"]
)
def update_user(user:user_dependancy, validated_user:validate_user_dependancy, db:db_dependancy):
    
    # ensure_valid_user_details(username=user_update.username,user_email=user_update.email,db=db)
    updated_user = database.update_user(
                    user_id=user.id,
                    user_email=validated_user.email, 
                    username=validated_user.username,
                    db=db    
                )
    return updated_user

# Verification handled by user dependancy
@app.delete(
    "/api/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["User"]
)
def delete_user(user:user_dependancy, db:db_dependancy):
    
    database.delete_user(user.id,db)
        
@app.get(
    "/api/users/{user_id}",
    response_model=UserResponse,
    tags=["User"],
)
def get_user(user:user_dependancy, db:db_dependancy):
    return user
    
@app.post(
    "/api/chronology/synthesize",
    response_model = SynthesisResponse,
    status_code = status.HTTP_201_CREATED,
    tags=["Case"],
)
async def create_case(db: db_dependancy, user_id:str, file:UploadFile = File(...)):
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
        record = database.save_case(
            case_id=case_id,
            user_id=user_id,
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
    tags=["Case"],
)
def get_case_by_id(case_id: str, db: db_dependancy):
    """Retrieves an existing synthesized clinical chronology by its unique case_id."""
    record = database.get_case_by_id(case_id,db)
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
def get_cases(db: db_dependancy):
    return database.list_all_cases(db)
 
@app.get(
    "/api/users/{user_id}/cases",
    response_model=List[CaseSummaryResponse],
    tags=["Dashboard"]
)
def get_cases_by_user_id(user_id:str, db: db_dependancy):
    return database.list_all_user_cases(user_id,db)   
    
@app.get(
    "/api/documents/{case_id}",
    tags=["Documents"]
)
def stream_document_pdf(case_id: str, db: db_dependancy):
    """Streams the raw PDF file to the frontend embedded PDF viewer."""
    record = database.get_case_by_id(case_id, db)
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

