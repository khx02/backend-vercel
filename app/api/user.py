from fastapi import APIRouter, Depends
from pymongo.asynchronous.database import AsyncDatabase
from app.db.client import get_db

from app.schemas.user import UserCreate, UserGet
from app.service.user import create_user_service

router = APIRouter()


@router.post("/", response_model=UserGet)
async def create_user(user: UserCreate, db: AsyncDatabase = Depends(get_db)):
    return await create_user_service(db, user)
