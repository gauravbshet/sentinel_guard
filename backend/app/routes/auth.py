from fastapi import APIRouter, HTTPException, status
import logging
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from ..database import get_db
from ..models.user_model import UserCreate, UserLogin
from ..utils.jwt_handler import create_access_token

import asyncio

router = APIRouter()
logger = logging.getLogger("uvicorn.error")

# Use bcrypt with proper configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__default_rounds=12
)


@router.post("/signup")
async def signup(payload: UserCreate):
    db = get_db()

    # If Supabase client is available, use Supabase Auth to create user
    client = getattr(db, "client", None)
    if client and hasattr(client, "auth"):
        try:
            # Supabase Python client sign_up is synchronous; run in thread
            def _signup():
                return client.auth.sign_up({"email": payload.email, "password": payload.password})

            res = await asyncio.to_thread(_signup)
            # res contains user and session info depending on Supabase config
            if hasattr(res, "error") and res.error:
                raise HTTPException(status_code=400, detail=str(res.error))
            # Some clients return a dict
            if isinstance(res, dict) and res.get("error"):
                raise HTTPException(
                    status_code=400, detail=str(res.get("error")))
            # return minimal info
            return {"email": payload.email}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Fallback: store user in DB (legacy)
    existing = await db.users.find_one({"email": payload.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Truncate password to 72 bytes for bcrypt compatibility
    password = payload.password.encode(
        'utf-8')[:72].decode('utf-8', errors='ignore')
    password_hash = pwd_context.hash(password)

    result = await db.users.insert_one({"email": payload.email, "password_hash": password_hash, "role": "admin"})
    return {"id": str(result.inserted_id), "email": payload.email}


@router.post("/login")
async def login(payload: UserLogin):
    db = get_db()

    client = getattr(db, "client", None)
    if client and hasattr(client, "auth"):
        try:
            def _signin():
                # newer supabase client uses sign_in_with_password
                if hasattr(client.auth, "sign_in_with_password"):
                    return client.auth.sign_in_with_password({"email": payload.email, "password": payload.password})
                # fallback to older method
                return client.auth.sign_in({"email": payload.email, "password": payload.password})

            res = await asyncio.to_thread(_signin)
            # res may contain session with access_token
            if isinstance(res, dict) and res.get("error"):
                raise HTTPException(
                    status_code=401, detail=str(res.get("error")))

            # attempt to extract access token and user id from common shapes
            token = None
            user_id = None

            if hasattr(res, "access_token"):
                token = getattr(res, "access_token")

            if isinstance(res, dict):
                # top-level fields
                token = token or res.get("access_token")
                # session nested
                session = res.get("session") or (res.get("data") or {}).get(
                    "session") if isinstance(res.get("data"), dict) else res.get("session")
                if isinstance(session, dict):
                    token = token or session.get("access_token")
                # user nested
                user = res.get("user") or (res.get("data") or {}).get(
                    "user") if isinstance(res.get("data"), dict) else res.get("user")
                if isinstance(user, dict):
                    user_id = user.get("id")
                # some clients return token under data.access_token
                if isinstance(res.get("data"), dict):
                    token = token or res.get("data").get("access_token")

            # If we found a token, return it.
            if token:
                return {"access_token": token, "token_type": "bearer"}

            # If Supabase didn't return an access token but returned a user id, issue a local JWT
            if user_id:
                jwt = create_access_token(str(user_id))
                return {"access_token": jwt, "token_type": "bearer", "source": "local_fallback"}

            # final fallback: indicate success but no token available
            # Log and return the raw response for debugging
            try:
                encoded = jsonable_encoder(res)
            except Exception:
                encoded = None

            # If jsonable_encoder produced a dict, try to find token there before returning raw
            if isinstance(encoded, dict):
                # look for session.access_token in encoded shapes
                session = encoded.get("session") or (
                    encoded.get("data") or {}).get("session")
                if isinstance(session, dict) and session.get("access_token"):
                    return {"access_token": session.get("access_token"), "token_type": session.get("token_type", "bearer"), "source": "supabase_session_extracted"}
                # some shapes put access_token at data.access_token
                if isinstance(encoded.get("data"), dict) and encoded.get("data").get("access_token"):
                    return {"access_token": encoded.get("data").get("access_token"), "token_type": "bearer", "source": "supabase_data_extracted"}

            # final: log and return raw for debugging
            try:
                encoded_for_log = encoded if encoded is not None else str(res)
            except Exception:
                encoded_for_log = str(res)
            logger.error(
                "Supabase signin response (no token): %s", encoded_for_log)
            return {"message": "signed_in", "raw": encoded_for_log}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Fallback legacy login
    user = await db.users.find_one({"email": payload.email})

    # Truncate password to 72 bytes for bcrypt compatibility
    password = payload.password.encode(
        'utf-8')[:72].decode('utf-8', errors='ignore')

    if not user or not pwd_context.verify(password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(str(user["_id"]))
    return {"access_token": token, "token_type": "bearer"}
