from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.asynchronous.database import AsyncDatabase
from app.db.client import get_db

from app.schemas.user import UserCreateReq, UserModel
from app.service.user import create_user_service

router = APIRouter()


@router.post("/register", response_model=UserModel)
async def create_user(
    user_create: UserCreateReq, db: AsyncDatabase = Depends(get_db)
) -> UserModel:
    try:
        return await create_user_service(db, user_create)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
