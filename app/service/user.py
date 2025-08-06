from app.schemas.user import UserCreateReq, UserModel, UserHashed
from app.db.user import create_user as db_create_user
from pymongo.asynchronous.database import AsyncDatabase

from app.core.security import hash_password
from app.core.constants import USERS_COLLECTION


# TODO: Handle duplicate email registration
async def create_user_service(
    db: AsyncDatabase, user_create: UserCreateReq
) -> UserModel:

    hashed_password = hash_password(user_create.password)

    user_hashed = UserHashed(email=user_create.email, hashed_password=hashed_password)

    user_in_db_dict = await db_create_user(db, user_hashed)
    return UserModel(
        id=user_in_db_dict["_id"],
        email=user_in_db_dict["email"],
        hashed_password=user_in_db_dict["hashed_password"],
    )


async def get_user_service(db: AsyncDatabase, email: str) -> UserModel | None:
    user_in_db = await db[USERS_COLLECTION].find_one({"email": email})
    if user_in_db:
        return UserModel(
            id=str(user_in_db["_id"]),
            email=user_in_db["email"],
            hashed_password=user_in_db["hashed_password"],
        )
    return None
