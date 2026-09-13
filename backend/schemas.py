from __future__ import annotations

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from models import MasterChronology

class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    username: str = Field(...,min_length=1, max_length=50,description="Name of the user to be displayed on the profile")
    email: str = Field(..., max_length=120, description="Email address of the user")

class UserCreate(UserBase):
    pass

# TODO: Include Cases here
class UserResponse(UserBase):
    id: str = Field(...,description="unique uuid identifier for user")
    image_file: Optional[str] = Field(default=None, description="Original image file.")
    image_path: str = Field(..., description="path of the image stored on the backend server")
    
class UserUpdate(UserBase):
    image_file: Optional[str] = Field(default=None, description="Original image file.")

class CaseBase(BaseModel):
    case_id: str = Field(...,description="Unique uuid identifier for this clinical case.")
    filename:str = Field(...,description="Original filename of the document.")
    total_pages:int = Field(...,description="Total pages processed from the pdf.")

class CaseSummaryResponse(CaseBase):
    model_config = ConfigDict(from_attributes=True)
    
    patient_name:Optional[str] = Field(default=None,description="Name of the patient.")
    patient_dob:Optional[str] = Field(default=None,description="Date of birth of the patient.")
    patient_age:Optional[int] = Field(default=None,description="Age of the patient.")
    event_count:int = Field(default=0,description="Number of total visits/labs and other medical encounters of the patient.")
    created_at:datetime = Field(...,description="The date case was created in the system.")    

# TODO: Might have to include user here  
class SynthesisResponse(CaseBase):
    model_config = ConfigDict(from_attributes=True)
    
    chronology: MasterChronology = Field(...,description="The synthesized clinical chronology")
    user_id: str = Field(...,description="User id of the person working on this case.")