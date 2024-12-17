from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime

class DetectionResponse(BaseModel):
    label: str
    confidence: float
    bbox: tuple
    indigenousTerm: Optional[str]

class ProcessImageResponse(BaseModel):
    success: bool
    detections: List[DetectionResponse]
    image_id: int

class TermResponse(BaseModel):
    id: int
    term: str
    language_code: str
    object_label: str
    pronunciation: Optional[str]
    context: Optional[str]
    verified: bool
    created_at: datetime

class LanguageCreate(BaseModel):
    code: str
    name: str
    region: Optional[str]

class TermCreate(BaseModel):
    language_id: int
    object_id: int
    term: str
    pronunciation: Optional[str]
    context: Optional[str]
    source: Optional[str]