from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserDB(BaseModel):
    id: Optional[str] = None
    email: EmailStr
    password_hash: str
    role: str = "admin"
