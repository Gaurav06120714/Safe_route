from pydantic import BaseModel
from typing import Optional, List

class Location(BaseModel):
    lat: float
    lng: float

class RouteRequest(BaseModel):
    start: Location
    end: Location
    time: Optional[str] = None  # HH:MM format
    user_id: Optional[str] = None

class HeatmapCell(BaseModel):
    min_lat: float
    max_lat: float
    min_lng: float
    max_lng: float
    risk_intensity: float
    segment_ids: List[str]
    average_safety: float

class CrimeReport(BaseModel):
    lat: float
    lng: float
    severity: int
    incident_type: str
    user_id: str
    timestamp: str
