"""
from app.schemas.user import UserCreateReq, UserModel, UserHashed
from app.db.user import create_user as db_create_user
from pymongo.asynchronous.database import AsyncDatabase

from app.core.security import hash_password
from app.core.constants import USERS_COLLECTION

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
"""

from app.schemas.kanban import KanbanModel, KanbanCreateReq
from app.db.kanban import create_kanban as db_create_kanban
from app.db.team import add_kanban_to_team as db_add_kanban_to_team
from pymongo.asynchronous.database import AsyncDatabase


async def create_kanban_service(
    db: AsyncDatabase, kanban_create: KanbanCreateReq
) -> KanbanModel:

    kanban_in_db_dict = await db_create_kanban(db, kanban_create)

    # Attach the kanban ID to the team which created it
    await db_add_kanban_to_team(db, kanban_create.team_id, kanban_in_db_dict["_id"])

    return KanbanModel(
        id=kanban_in_db_dict["_id"],
        name=kanban_in_db_dict["name"],
    )
