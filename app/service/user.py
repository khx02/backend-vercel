from app.schemas.user import UserCreate, UserGet
from app.db.user import create_user as db_create_user
from pymongo.asynchronous.database import AsyncDatabase


async def create_user_service(db: AsyncDatabase, user: UserCreate) -> UserGet:
    user_dict = await db_create_user(db, user)
    return UserGet(id=user_dict["_id"], email=user_dict["email"])
