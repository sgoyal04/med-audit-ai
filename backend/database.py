"""
database.py: Persistent storage for medaudit.ai
"""
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy import select
from sqlalchemy.types import JSON
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session

DATABASE_URL = "sqlite+pysqlite:///app.db"

engine = create_engine(
    DATABASE_URL, 
    echo=True, 
    connect_args={"check_same_thread":False},
)

SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

class Base(DeclarativeBase):
    pass

class CaseRecord(Base):
    __tablename__ = "cases"
    
    case_id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    total_pages = Column(Integer, nullable=False)
    file_path = Column(String, nullable=False)
    patient_name = Column(String, nullable=True, index=True)
    patient_dob = Column(String, nullable=True)
    patient_age = Column(String, nullable=True)
    chronology = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda:datetime.now(timezone.utc))
    
def init_db():
    Base.metadata.create_all(bind=engine)
    
def get_db():
    """FastAPI dependency for database session management."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    
def save_case(
    case_id: str, 
    filename:str,
    total_pages:int,
    file_path:str,
    patient_name:str,
    patient_dob:str,
    patient_age:int,
    chronology_dict: Dict[str,Any],
    db: Session
):
    record = CaseRecord(
        case_id=case_id,
        filename=filename,
        total_pages=total_pages,
        file_path=file_path, 
        patient_name=patient_name,
        patient_dob=patient_dob,
        patient_age=patient_age,
        chronology=chronology_dict,
    )
    db.merge(record)
    db.commit()
    return record
            
def get_case_by_id(case_id: str, db:Session) -> Optional[Dict[str, Any]]:
    """ Returns the specific case details."""
    
    return db.get(CaseRecord, case_id)
    

def list_all_cases(db: Session) -> List[Dict[str, Any]]:
    """Lists all historical clinical cases for the audit dashboard."""
    stmt = select(
        CaseRecord.case_id, 
        CaseRecord.filename, 
        CaseRecord.total_pages,
        CaseRecord.patient_name, 
        CaseRecord.patient_age,
        CaseRecord.patient_dob,
        CaseRecord.chronology,
        CaseRecord.created_at,
    )

    results = []
    for row in db.execute(stmt).mappings().all():
        record = dict(row)
        chronology_data = record.pop("chronology", {})
        
        # If chronology is a dict (from MasterChronology.model_dump()), 
        # extract the list of events (usually under 'events' or 'timeline')
        if isinstance(chronology_data, dict):
            events = chronology_data.get("events") or chronology_data.get("timeline") or []
            record["event_count"] = len(events)
        elif isinstance(chronology_data, list):
            record["event_count"] = len(chronology_data)
        else:
            record["event_count"] = 0
            
        results.append(record)
        
    return results