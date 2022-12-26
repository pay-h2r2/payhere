from datetime import datetime
from pydantic import BaseModel


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str


class UserLogin(UserCreate):
    pass


class User(UserBase):
    id: int
    hashed_password: str
    salt: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
