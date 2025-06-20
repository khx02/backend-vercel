from pydantic import BaseModel


class UserCreate(BaseModel):
    email: str


class UserGet(BaseModel):
    id: str
    email: str
