from pymongo.asynchronous.database import AsyncDatabase
from app.schemas.user import UserHashed
from typing import Dict, Any

USERS_COLLECTION = "users"


async def create_user(db: AsyncDatabase, user_hashed: UserHashed) -> Dict[str, Any]:
    user_hashed_dict = user_hashed.model_dump()
    result = await db[USERS_COLLECTION].insert_one(user_hashed_dict)
    user_hashed_dict["_id"] = str(result.inserted_id)
    return user_hashed_dict
