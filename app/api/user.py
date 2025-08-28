from fastapi import APIRouter, Depends
from pymongo.asynchronous.database import AsyncDatabase

from app.api.auth import get_current_user
from app.db.client import get_db
from app.schemas.user import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    CreateUserRequest,
    CreateUserResponse,
    GetCurrentUserTeamsResponse,
    UserModel,
    VerifyCodeRequest,
    VerifyCodeResponse,
)
from app.service.user import (
    change_password_service,
    create_user_service,
    get_current_user_teams_service,
    verify_code_service,
)

router = APIRouter()


@router.post("/register")
async def create_user(
    create_user_request: CreateUserRequest, db: AsyncDatabase = Depends(get_db)
) -> CreateUserResponse:
    return await create_user_service(create_user_request, db)


@router.post("/verify-code")
async def verify_code(
    verify_code_request: VerifyCodeRequest, db: AsyncDatabase = Depends(get_db)
) -> VerifyCodeResponse:
    return await verify_code_service(verify_code_request, db)


@router.get("/get-current-user-teams")
async def get_current_user_teams(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncDatabase = Depends(get_db),
) -> GetCurrentUserTeamsResponse:
    return await get_current_user_teams_service(current_user.id, db)


@router.post("/change-password")
async def change_password(
    change_password_request: ChangePasswordRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncDatabase = Depends(get_db),
) -> ChangePasswordResponse:
    return await change_password_service(current_user.id, change_password_request, db)
