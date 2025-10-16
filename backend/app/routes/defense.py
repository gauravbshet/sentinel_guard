from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import os
import psutil
from ..utils.encryption import encrypt_bytes

router = APIRouter()


class DefensePayload(BaseModel):
    action: str  # kill_process | encrypt_file
    pid: int | None = None
    file_path: str | None = None


@router.post("/trigger")
async def trigger_defense(payload: DefensePayload):
    if payload.action == "kill_process":
        if payload.pid is None:
            raise HTTPException(status_code=400, detail="pid required")
        try:
            proc = psutil.Process(payload.pid)
            proc.terminate()
            return {"status": "terminated", "pid": payload.pid}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    elif payload.action == "encrypt_file":
        if not payload.file_path:
            raise HTTPException(status_code=400, detail="file_path required")
        if not os.path.isfile(payload.file_path):
            raise HTTPException(status_code=404, detail="file not found")
        try:
            with open(payload.file_path, "rb") as f:
                data = f.read()
            nonce, ciphertext = encrypt_bytes(data)
            with open(payload.file_path + ".enc", "wb") as f:
                f.write(nonce + ciphertext)
            return {"status": "encrypted", "output": payload.file_path + ".enc"}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        raise HTTPException(status_code=400, detail="unknown action")
