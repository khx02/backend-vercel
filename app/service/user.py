from app.schemas.user import UserCreateReq, UserModel, UserHashed
from app.db.user import (
    create_user as db_create_user,
    get_user_by_email as db_get_user_by_email,
)
from pymongo.asynchronous.database import AsyncDatabase

from app.core.security import hash_password
from app.core.constants import USERS_COLLECTION


async def create_user_service(
    db: AsyncDatabase, user_create: UserCreateReq
) -> UserModel:

    existing_user = await db_get_user_by_email(db, user_create.email)
    if existing_user:
        raise ValueError(f"User with email '{user_create.email}' already exists")

    hashed_password = hash_password(user_create.password)

    user_hashed = UserHashed(email=user_create.email, hashed_password=hashed_password)

    user_in_db_dict = await db_create_user(db, user_hashed)
    return UserModel(
        id=user_in_db_dict["_id"],
        email=user_in_db_dict["email"],
        hashed_password=user_in_db_dict["hashed_password"],
    )
