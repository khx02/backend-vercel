from pydantic import BaseModel, EmailStr


class UserCreateReq(BaseModel):
    email: EmailStr
    password: str


class UserHashed(BaseModel):
    email: EmailStr
    hashed_password: str


class UserModel(BaseModel):
    id: str
    email: EmailStr
    hashed_password: str


class UserRes(BaseModel):
    email: EmailStr
