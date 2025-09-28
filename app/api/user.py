from fastapi import APIRouter, Depends
from pymongo.asynchronous.database import AsyncDatabase

from app.api.auth import get_current_user_info
from app.db.client import get_db
from app.schemas.user import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    CreateUserRequest,
    CreateUserResponse,
    GetCurrentUserResponse,
    GetCurrentUserTeamsResponse,
    GetUserByIdResponse,
    UserModel,
    VerifyCodeRequest,
    VerifyCodeResponse,
)
from app.service.user import (
    change_password_service,
    create_user_service,
    get_current_user_teams_service,
    get_user_by_id_service,
    verify_code_service,
)
from app.service.user import get_users_by_ids_service
from typing import List
from fastapi import Body

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


@router.get("/get-current-user")
async def get_current_user(
    current_user: UserModel = Depends(get_current_user_info),
) -> GetCurrentUserResponse:
    return GetCurrentUserResponse(user=current_user)


@router.get("/get-user-by-id/{user_id}")
async def get_user_by_id(
    user_id: str,
    db: AsyncDatabase = Depends(get_db),
) -> GetUserByIdResponse:
    user = await get_user_by_id_service(user_id, db)
    return GetUserByIdResponse(user=user)


@router.get("/get-current-user-teams")
async def get_current_user_teams(
    current_user: UserModel = Depends(get_current_user_info),
    db: AsyncDatabase = Depends(get_db),
) -> GetCurrentUserTeamsResponse:
    return await get_current_user_teams_service(current_user.id, db)


@router.post("/get-users-by-ids")
async def get_users_by_ids(
    user_ids: List[str] = Body(..., embed=True),
    _: UserModel = Depends(get_current_user_info),
    db: AsyncDatabase = Depends(get_db),
) -> list[UserModel]:
    return await get_users_by_ids_service(user_ids, db)


@router.post("/change-password")
async def change_password(
    change_password_request: ChangePasswordRequest,
    current_user: UserModel = Depends(get_current_user_info),
    db: AsyncDatabase = Depends(get_db),
) -> ChangePasswordResponse:
    return await change_password_service(current_user.id, change_password_request, db)
