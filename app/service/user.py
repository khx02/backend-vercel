from app.schemas.user import UserCreateReq, UserModel, UserHashed, ChangePasswordReq
from app.db.user import (
    create_user as db_create_user,
    get_user_by_email as db_get_user_by_email,
    update_password as db_update_password,
)
from pymongo.asynchronous.database import AsyncDatabase

from app.core.security import hash_password, verify_password
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


async def get_user_service(db: AsyncDatabase, email: str) -> UserModel | None:
    user_in_db = await db_get_user_by_email(db, email)
    if user_in_db:
        return UserModel(
            id=str(user_in_db["_id"]),
            email=user_in_db["email"],
            hashed_password=user_in_db["hashed_password"],
        )
    return None


async def change_password_service(
    db: AsyncDatabase, change_password: ChangePasswordReq, current_user_email: str
) -> UserModel | None:

    user_in_db = await get_user_service(db, current_user_email)
    if not user_in_db:  # This should not happen as the user should be authenticated
        raise ValueError("User not found")

    if not verify_password(change_password.old_password, user_in_db.hashed_password):
        raise ValueError("Old password is incorrect")

    new_hashed_password = hash_password(change_password.new_password)

    await db_update_password(db, current_user_email, new_hashed_password)

    user_in_db.hashed_password = new_hashed_password
    return user_in_db
