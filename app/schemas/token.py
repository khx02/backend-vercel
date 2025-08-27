from pydantic import BaseModel, EmailStr


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    access_expires_at: float
    refresh_expires_at: float
    token_type: str


class UserRes(BaseModel):
    email: EmailStr


class TokenRes(BaseModel):
    # token: TokenPair
    user: UserRes
    token_type: str = "bearer"
    access_token: str


class TokenData(BaseModel):
    email: EmailStr


class ValidateTokenRes(BaseModel):
    is_valid: bool


class RefreshTokenReq(BaseModel):
    token: str
