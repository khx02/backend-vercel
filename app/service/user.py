from annotated_types import T
from fastapi import HTTPException
from pymongo.asynchronous.database import AsyncDatabase

from app.core.security import hash_password, verify_password
from app.db.user import (
    db_create_user,
    db_get_user_by_id,
    db_get_user_teams_by_id,
    db_get_user_by_email,
    db_update_password,
)
from app.schemas.team import TeamModel
from app.schemas.user import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    CreateUserRequest,
    CreateUserResponse,
    GetCurrentUserTeamsResponse,
    UserModel,
)


async def create_user_service(
    create_user_request: CreateUserRequest, db: AsyncDatabase
) -> CreateUserResponse:
    existing_user = await db_get_user_by_email(create_user_request.email, db)
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
    existing_user = await db_get_user_by_id(current_user_id, db)
    if not existing_user:
        raise HTTPException(
            status_code=404, detail=f"User not found: id={current_user_id}"
        )

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


async def change_password_service(
    current_user_id: str,
    change_password_request: ChangePasswordRequest,
    db: AsyncDatabase,
) -> ChangePasswordResponse:
    user_in_db = await db_get_user_by_id(current_user_id, db)
    if not user_in_db:
        raise HTTPException(
            status_code=404, detail=f"User not found: id={current_user_id}"
        )

    hashed_password = user_in_db["hashed_password"]

    if not verify_password(change_password_request.old_password, hashed_password):
        raise HTTPException(
            status_code=400,
            detail=f"Incorrect old password, please try again: id={current_user_id}",
        )

    new_hashed_password = hash_password(change_password_request.new_password)

    await db_update_password(current_user_id, new_hashed_password, db)

    return ChangePasswordResponse()
