from typing import Any, Dict, List

from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from app.core.common import stringify_object_ids
from app.core.constants import USERS_COLLECTION, TEAMS_COLLECTION
from app.schemas.user import UserHashed


async def create_user(
    db: AsyncDatabase, user_hashed: UserHashed
) -> Dict[str, Any] | None:
    try:
        user_hashed_dict = user_hashed.model_dump()
        result = await db[USERS_COLLECTION].insert_one(user_hashed_dict)
        user_hashed_dict["_id"] = result.inserted_id

        return stringify_object_ids(user_hashed_dict)
    except Exception as e:
        return None


async def db_get_user_teams_by_id(
    user_id: str, db: AsyncDatabase
) -> List[Dict[str, Any]]:
    try:
        teams = (
            await db[TEAMS_COLLECTION]
            .find({"member_ids": ObjectId(user_id)})
            .to_list(length=None)
        )
        return [stringify_object_ids(team) for team in teams]
    except Exception as e:
        return []


async def get_user_by_email(db: AsyncDatabase, email: str) -> Dict[str, Any] | None:
    try:
        user_dict = await db[USERS_COLLECTION].find_one({"email": email})
        if user_dict:
            return stringify_object_ids(user_dict)
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
