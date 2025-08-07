from pymongo.asynchronous.database import AsyncDatabase
from app.schemas.user import UserHashed
from typing import Dict, Any

from app.core.constants import USERS_COLLECTION


async def create_user(db: AsyncDatabase, user_hashed: UserHashed) -> Dict[str, Any]:
    user_hashed_dict = user_hashed.model_dump()
    result = await db[USERS_COLLECTION].insert_one(user_hashed_dict)
    user_hashed_dict["_id"] = str(result.inserted_id)
    return user_hashed_dict


async def get_user_by_email(db: AsyncDatabase, email: str) -> Dict[str, Any] | None:
    try:
        user_dict = await db[USERS_COLLECTION].find_one({"email": email})
        if user_dict:
            user_dict["_id"] = str(user_dict["_id"])
            return user_dict
        return None
    except Exception as e:
        return None
