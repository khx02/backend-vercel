from annotated_types import T
from fastapi import HTTPException
from pymongo.asynchronous.database import AsyncDatabase

from app.core.constants import USERS_COLLECTION
from app.core.security import hash_password, verify_password
from app.db.user import db_create_user, db_get_user_teams_by_id, get_user_by_email as db_get_user_by_email
from app.db.user import update_password as db_update_password
from app.schemas.team import TeamModel
from app.schemas.user import (
    ChangePasswordReq,
    CreateUserRequest,
    CreateUserResponse,
    GetCurrentUserTeamsResponse,
    UserModel,
)


async def create_user_service(
    create_user_request: CreateUserRequest, db: AsyncDatabase
) -> CreateUserResponse:

    existing_user = await db_get_user_by_email(db, create_user_request.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail=f"A user has already been created using this email address: email={create_user_request.email}",
        )

    hashed_password = hash_password(create_user_request.password)

    user_in_db_dict = await db_create_user(create_user_request, hashed_password, db)

    return CreateUserResponse(
        user=UserModel(
            id=user_in_db_dict["_id"],
            email=user_in_db_dict["email"],
        )
    )


async def get_current_user_teams_service(
    current_user_id: str,
    db: AsyncDatabase,
) -> GetCurrentUserTeamsResponse:

    team_models_in_db = await db_get_user_teams_by_id(current_user_id, db)

    return GetCurrentUserTeamsResponse(
        teams=[
            TeamModel(
                id=str(team["_id"]),
                name=team["name"],
                member_ids=team["member_ids"],
                exec_member_ids=team["exec_member_ids"],
                project_ids=team["project_ids"],
            )
            for team in team_models_in_db
        ]
    )


async def get_user_service(db: AsyncDatabase, email: str) -> UserModel | None:
    user_in_db = await db_get_user_by_email(db, email)
    if user_in_db:
        return UserModel(
            id=str(user_in_db["_id"]),
            email=user_in_db["email"],
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
