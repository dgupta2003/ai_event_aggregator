from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Event(BaseModel):
    source: str
    title: str
    url: str
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    is_virtual: Optional[bool] = None
    price: Optional[str] = None
    raw: Optional[dict] = None

class Query(BaseModel):
    id: int
    text: str
    filters: dict = Field(default_factory=dict)

class ResultRow(BaseModel):
    query_id: int
    engine: str
    response_time_ms: int
    accuracy: float
    coverage: int
    source_diversity: int
    freshness_ok: int
