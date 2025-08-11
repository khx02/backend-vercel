from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import create_token_pair
from app.schemas.token import TokenRes
from pymongo.asynchronous.database import AsyncDatabase
from app.db.client import get_db

from app.schemas.user import UserCreateReq, UserModel, UserRes
from app.service.user import create_user_service

router = APIRouter()


@router.post("/register", response_model=UserModel)
async def create_user(
    user_create: UserCreateReq, db: AsyncDatabase = Depends(get_db)
) -> TokenRes:
    try:
        user =  await create_user_service(db, user_create)
        token_pair = create_token_pair(data={"sub": user.email})
        return TokenRes(
            token=token_pair,
            user=UserRes(email=user.email),
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
