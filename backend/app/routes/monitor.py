from fastapi import APIRouter
from ..database import get_db
from ..utils.monitor import collect_system_metrics

router = APIRouter()


@router.get("/system")
async def get_system_metrics():
    return collect_system_metrics()


@router.get("/logs")
async def get_logs(limit: int = 50):
    db = get_db()
    cursor = db.anomaly_logs.find().sort("timestamp", -1).limit(limit)
    logs = []
    async for doc in cursor:
        doc["id"] = str(doc.pop("_id", ""))
        logs.append(doc)
    return {"logs": logs}
