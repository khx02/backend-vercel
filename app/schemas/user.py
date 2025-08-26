from pydantic import BaseModel, EmailStr, field_validator

from app.schemas.team import TeamModel


def is_valid_password(password: str) -> str:
    if len(password) < 6:
        raise ValueError("Password must be at least 6 characters long")
    return password


class UserModel(BaseModel):
    id: str
    email: EmailStr


class CreateUserRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    def validate_password(cls, password: str) -> str:
        return is_valid_password(password)


class CreateUserResponse(BaseModel):
    user: UserModel


class UserHashed(BaseModel):
    email: EmailStr
    hashed_password: str


class UserRes(BaseModel):
    email: EmailStr


class GetCurrentUserTeamsRequest(BaseModel):
    pass


class GetCurrentUserTeamsResponse(BaseModel):
    teams: list[TeamModel]


class ChangePasswordReq(BaseModel):
    old_password: str
    new_password: str

    @field_validator("new_password")
    def validate_new_password(cls, new_password: str) -> str:
        return is_valid_password(new_password)
