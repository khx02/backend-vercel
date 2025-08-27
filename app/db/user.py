from typing import Any, Dict, List

from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from app.core.common import stringify_object_ids
from app.core.constants import USERS_COLLECTION, TEAMS_COLLECTION
from app.schemas.user import CreateUserRequest


async def db_create_user(
    create_user_request: CreateUserRequest, hashed_password: str, db: AsyncDatabase
) -> Dict[str, Any]:
    user_dict = {"email": create_user_request.email, "hashed_password": hashed_password}

    result = await db[USERS_COLLECTION].insert_one(user_dict)
    user_dict["_id"] = result.inserted_id

    return stringify_object_ids(user_dict)


async def db_get_user_teams_by_id(
    user_id: str, db: AsyncDatabase
) -> List[Dict[str, Any]]:
    teams = (
        await db[TEAMS_COLLECTION]
        .find({"member_ids": ObjectId(user_id)})
        .to_list(length=None)
    )
    return [stringify_object_ids(team) for team in teams]


async def db_get_user_by_id(user_id: str, db: AsyncDatabase) -> Dict[str, Any]:
    user_dict = await db[USERS_COLLECTION].find_one({"_id": ObjectId(user_id)})
    return stringify_object_ids(user_dict)


async def db_get_user_by_email(email: str, db: AsyncDatabase) -> Dict[str, Any]:
    user_dict = await db[USERS_COLLECTION].find_one({"email": email})
    return stringify_object_ids(user_dict)


# Special function for cookie based authentication, which requires a query for a user
# which may not exist, so cannot assume correctness before calling
async def db_get_user_or_none_by_email(
    email: str, db: AsyncDatabase
) -> Dict[str, Any] | None:
    user_dict = await db[USERS_COLLECTION].find_one({"email": email})
    return stringify_object_ids(user_dict) if user_dict else None


async def db_update_password(
    current_user_id: str, new_hashed_password: str, db: AsyncDatabase
) -> None:
    await db[USERS_COLLECTION].update_one(
        {"_id": ObjectId(current_user_id)},
        {"$set": {"hashed_password": new_hashed_password}},
    )
