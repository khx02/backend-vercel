from pymongo.asynchronous.database import AsyncDatabase
from app.schemas.user import UserCreate

USER_COLLECTION = "users"


async def create_user(db: AsyncDatabase, user: UserCreate) -> dict:
    user_dict = user.model_dump()
    result = await db[USER_COLLECTION].insert_one(user_dict)
    user_dict["_id"] = str(result.inserted_id)
    return user_dict
