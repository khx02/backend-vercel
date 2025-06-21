from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserHashed(BaseModel):
    email: EmailStr
    hashed_password: str


class UserGet(BaseModel):
    id: str
    email: EmailStr
    hashed_password: str