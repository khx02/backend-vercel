from pymongo.asynchronous.database import AsyncDatabase
from app.schemas.user import UserHashed

USER_COLLECTION = "users"


async def create_user(db: AsyncDatabase, user_hashed: UserHashed) -> dict:
    user_hashed_dict = user_hashed.model_dump()
    result = await db[USER_COLLECTION].insert_one(user_hashed_dict)
    user_hashed_dict["_id"] = str(result.inserted_id)
    return user_hashed_dict
