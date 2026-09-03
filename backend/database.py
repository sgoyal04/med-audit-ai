"""
database.py: Persistent storage for medaudit.ai
"""

from __future__ import annotations
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from sqlalchemy import create_engine, String, Integer, DateTime
from sqlalchemy import select, ForeignKey
from sqlalchemy.types import JSON
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


DATABASE_URL = "sqlite+pysqlite:///app.db"

engine = create_engine(
    DATABASE_URL, 
    echo=True, 
    connect_args={"check_same_thread":False},
)

SessionLocal = sessionmaker(autocommit=False,autoflush=False,bind=engine)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    image_file: Mapped[str | None] = mapped_column(String(200), nullable=True, default=None)

    cases: Mapped[list["CaseRecord"]] = relationship("CaseRecord", back_populates="user")

    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"media/profile_pics/{self.image_file}"
        return "/static/profile_pics/default.jpg"

class CaseRecord(Base):
    __tablename__ = "cases"
    
    case_id: Mapped[str] = mapped_column(String, primary_key=True, index=True)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    total_pages: Mapped[int]= mapped_column(Integer, nullable=False)
    file_path: Mapped[str] = mapped_column(String, nullable=False)
    patient_name: Mapped[str] = mapped_column(String, nullable=True, index=True)
    patient_dob: Mapped[str] = mapped_column(String, nullable=True)
    patient_age: Mapped[str] = mapped_column(String, nullable=True)
    chronology: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda:datetime.now(timezone.utc))
    
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"),nullable=True,index=True,default=None)
    user: Mapped[User | None] = relationship("User", back_populates="cases")
    
def init_db():
    Base.metadata.create_all(bind=engine)
    
def get_db():
    """FastAPI dependency for database session management."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# TODO: image_file and cases 
def create_new_user(user_id:str, username:str, user_email:str, db:Session) -> User:
    user = User(
        id=user_id,
        username=username,
        email=user_email,
        image_file=None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_user_by_id(user_id:str, db:Session) -> User:
    stmt = select(User).where(User.id==user_id)
    user = db.execute(stmt).scalars().first()
    return user

def get_user_by_name(username:str, db:Session) -> User:
    stmt = select(User).where(User.username==username)
    user = db.execute(stmt).scalars().first()
    return user

def get_user_by_email(user_email:str, db:Session) -> User:
    stmt = select(User).where(User.email==user_email)
    user = db.execute(stmt).scalars().first()
    return user

def update_user(user_id:str, username:str, user_email:str,image_file:str, db:Session) -> User:
    stmt = select(User).where(User.id == user_id)
    user = db.execute(stmt).scalars().first()
    user.username = username
    user.email = user_email
    if image_file is not None:
        user.image_file = image_file
    db.commit()
    db.refresh(user)
    return user

def delete_user(user_id:str, db:Session):
    stmt = select(User).where(User.id == user_id)
    user = db.execute(stmt).scalars().first()
    db.delete(user)
    db.commit()

def save_case(
    case_id: str, 
    user_id:str,
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
        user_id=user_id,
        filename=filename,
        total_pages=total_pages,
        file_path=file_path, 
        patient_name=patient_name,
        patient_dob=patient_dob,
        patient_age=patient_age,
        chronology=chronology_dict,
    )
    db.add(record)
    db.commit()
    return record
            
def get_case_by_id(case_id: str, db:Session) -> Optional[Dict[str, Any]]:
    """ Returns the specific case details."""
    
    return db.get(CaseRecord, case_id)
    
def get_cases(stmt,db:Session):
    results = []
    for row in db.execute(stmt).mappings().all():
        record = dict(row)
        chronology_data = record.pop("chronology", {})
        
        # If chronology is a dict (from MasterChronology.model_dump()), 
        # extract the list of events
        # TODO: Do we need timeline??
        if isinstance(chronology_data, dict):
            events = chronology_data.get("events") or chronology_data.get("timeline") or []
            record["event_count"] = len(events)
        elif isinstance(chronology_data, list):
            record["event_count"] = len(chronology_data)
        else:
            record["event_count"] = 0
            
        results.append(record)
        
    return results

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
    return get_cases(stmt=stmt,db=db)

def list_all_user_cases(user_id:str, db:Session) -> List[Dict[str, Any]]:
    """Lists all historical clinical cases created by the user."""
    stmt = select(
        CaseRecord.case_id, 
        CaseRecord.filename, 
        CaseRecord.total_pages,
        CaseRecord.patient_name, 
        CaseRecord.patient_age,
        CaseRecord.patient_dob,
        CaseRecord.chronology,
        CaseRecord.created_at,
    ).where(CaseRecord.user_id==user_id)
    
    return get_cases(stmt=stmt,db=db)
    