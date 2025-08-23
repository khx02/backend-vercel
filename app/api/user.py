from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.asynchronous.database import AsyncDatabase

from app.api.auth import get_current_user
from app.db.client import get_db
from app.schemas.user import (
    ChangePasswordReq,
    GetCurrentUserTeamsResponse,
    UserCreateReq,
    UserModel,
)
from app.service.user import (
    change_password_service,
    create_user_service,
    get_current_user_teams_service,
)

router = APIRouter()


@router.post("/register", response_model=UserModel)
async def create_user(
    user_create: UserCreateReq, db: AsyncDatabase = Depends(get_db)
) -> UserModel | None:
    try:
        user = await create_user_service(db, user_create)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/get-user-teams")
async def get_current_user_teams(
    current_user: UserModel = Depends(get_current_user),
    db: AsyncDatabase = Depends(get_db),
) -> GetCurrentUserTeamsResponse:
    return get_current_user_teams_service(current_user, db)


@router.post("/change_password", response_model=UserModel)
async def change_password(
    change_password: ChangePasswordReq,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncDatabase = Depends(get_db),
) -> UserModel | None:
    try:
        return await change_password_service(db, change_password, current_user.email)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to change password",
        )
