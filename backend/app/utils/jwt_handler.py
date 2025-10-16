import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt


JWT_SECRET = os.getenv("JWT_SECRET", "dev_secret_change_me")
JWT_ALGORITHM = "HS256"
JWT_EXPIRES_MIN = int(os.getenv("JWT_EXPIRES_MIN", "60"))


def create_access_token(subject: str, extra_claims: Optional[Dict[str, Any]] = None) -> str:
    now = datetime.now(tz=timezone.utc)
    payload: Dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=JWT_EXPIRES_MIN)).timestamp()),
    }
    if extra_claims:
        payload.update(extra_claims)
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def verify_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
