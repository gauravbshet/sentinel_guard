from fastapi import APIRouter
from pydantic import BaseModel
from ..utils.ml_model import predict_anomaly
from ..utils.monitor import collect_system_metrics
from ..database import get_db
from ..models.anomaly_log import AnomalyLog

router = APIRouter()


class MetricsPayload(BaseModel):
    cpu_percent: float | None = None
    memory_percent: float | None = None
    net_bytes_sent: float | None = None
    net_bytes_recv: float | None = None


@router.post("/detect")
async def detect_anomaly(payload: MetricsPayload | None = None):
    metrics = payload.model_dump(
        exclude_none=True) if payload else collect_system_metrics()
    result = predict_anomaly(metrics)
    # Store log
    db = get_db()
    # Use pydantic json-mode dump to ensure datetime is serialized to ISO string
    log = AnomalyLog(
        metrics=metrics, score=result["score"], label=result["label"]).model_dump(mode="json")
    await db.anomaly_logs.insert_one(log)
    return {"metrics": metrics, **result}
