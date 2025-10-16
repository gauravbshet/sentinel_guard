from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from ..database import get_db
from ..models.user_model import UserCreate, UserLogin
from ..utils.jwt_handler import create_access_token

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.post("/signup")
async def signup(payload: UserCreate):
    db = get_db()
    existing = await db.users.find_one({"email": payload.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    password_hash = pwd_context.hash(payload.password)
    result = await db.users.insert_one({"email": payload.email, "password_hash": password_hash, "role": "admin"})
    return {"id": str(result.inserted_id), "email": payload.email}


@router.post("/login")
async def login(payload: UserLogin):
    db = get_db()
    user = await db.users.find_one({"email": payload.email})
    if not user or not pwd_context.verify(payload.password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(str(user["_id"]))
    return {"access_token": token, "token_type": "bearer"}
