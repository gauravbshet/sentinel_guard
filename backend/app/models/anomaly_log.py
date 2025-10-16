from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from datetime import datetime


class AnomalyLog(BaseModel):
    id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metrics: Dict[str, Any]
    score: float
    label: str  # normal/anomaly
    action_taken: Optional[str] = None
