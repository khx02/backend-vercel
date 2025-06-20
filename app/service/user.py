from app.schemas.user import UserCreate, UserGet, UserHashed
from app.db.user import create_user as db_create_user
from pymongo.asynchronous.database import AsyncDatabase

from app.core.security import hash_password


async def create_user_service(db: AsyncDatabase, user_create: UserCreate) -> UserGet:

    hashed_password = hash_password(user_create.password)

    user_hashed = UserHashed(email=user_create.email, hashed_password=hashed_password)

    user_in_db_dict = await db_create_user(db, user_hashed)
    return UserGet(id=user_in_db_dict["_id"], email=user_in_db_dict["email"])
