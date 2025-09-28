from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator

from app.schemas.team import TeamModel


def is_valid_password(password: str) -> str:
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters long")
    return password


class UserModel(BaseModel):
    id: str
    email: EmailStr
    first_name: str = ""
    last_name: str = ""


class PendingVerification(BaseModel):
    email: EmailStr
    verification_code: str
    hashed_password: str
    created_at: datetime
    first_name: str
    last_name: str


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    send_email: bool = True

    @field_validator("password")
    def validate_password(cls, password: str) -> str:
        return is_valid_password(password)


class CreateUserResponse(BaseModel):
    pass


class VerifyCodeRequest(BaseModel):
    email: EmailStr
    verification_code: str


class VerifyCodeResponse(BaseModel):
    user: UserModel


class GetCurrentUserRequest(BaseModel):
    pass


class GetCurrentUserResponse(BaseModel):
    user: UserModel


class GetCurrentUserTeamsRequest(BaseModel):
    pass


class GetUserByIdRequest(BaseModel):
    pass


class GetUserByIdResponse(BaseModel):
    user: UserModel


class GetCurrentUserTeamsResponse(BaseModel):
    teams: list[TeamModel]


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

    @field_validator("new_password")
    def validate_new_password(cls, new_password: str) -> str:
        return is_valid_password(new_password)


class ChangePasswordResponse(BaseModel):
    pass
