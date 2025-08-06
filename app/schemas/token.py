from pydantic import BaseModel, EmailStr

from app.schemas.user import UserRes


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    access_expires_at: float
    refresh_expires_at: float
    token_type: str


# Response when client requests a new/renewal of a token
class TokenRes(BaseModel):
    token: TokenPair
    user: UserRes
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    email: EmailStr
