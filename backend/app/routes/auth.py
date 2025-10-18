from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from ..database import get_db
from ..models.user_model import UserCreate, UserLogin
from ..utils.jwt_handler import create_access_token

router = APIRouter()

# Use bcrypt with proper configuration
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__default_rounds=12
)


@router.post("/signup")
async def signup(payload: UserCreate):
    db = get_db()
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
    user = await db.users.find_one({"email": payload.email})

    # Truncate password to 72 bytes for bcrypt compatibility
    password = payload.password.encode(
        'utf-8')[:72].decode('utf-8', errors='ignore')

    if not user or not pwd_context.verify(password, user.get("password_hash", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(str(user["_id"]))
    return {"access_token": token, "token_type": "bearer"}
