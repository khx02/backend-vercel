from typing import Any, Dict

from pymongo.asynchronous.database import AsyncDatabase

from app.core.constants import USERS_COLLECTION
from app.schemas.user import UserHashed


async def create_user(
    db: AsyncDatabase, user_hashed: UserHashed
) -> Dict[str, Any] | None:
    try:
        user_hashed_dict = user_hashed.model_dump()
        result = await db[USERS_COLLECTION].insert_one(user_hashed_dict)
        user_hashed_dict["_id"] = str(result.inserted_id)
        return user_hashed_dict
    except Exception as e:
        return None


async def get_user_by_email(db: AsyncDatabase, email: str) -> Dict[str, Any] | None:
    try:
        user_dict = await db[USERS_COLLECTION].find_one({"email": email})
        if user_dict:
            user_dict["_id"] = str(user_dict["_id"])
            return user_dict
        return None
    except Exception as e:
        return None


async def update_password(
    db: AsyncDatabase, current_user_email: str, new_hashed_password: str
) -> None:
    await db[USERS_COLLECTION].update_one(
        {"email": current_user_email},
        {"$set": {"hashed_password": new_hashed_password}},
    )
