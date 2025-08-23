from bson import ObjectId
from fastapi import HTTPException
from pymongo.asynchronous.database import AsyncDatabase

from app.db.team import create_team as db_create_team, db_create_project
from app.db.team import get_team_by_id as db_get_team_by_id
from app.db.team import join_team as db_join_team
from app.db.team import kick_team_member as db_kick_team_member
from app.db.team import leave_team as db_leave_team
from app.db.team import promote_team_member as db_promote_team_member
from app.schemas.project import Project, TodoStatus
from app.schemas.team import (
    CreateProjectRequest,
    CreateProjectResponse,
    GetTeamResponse,
    KickTeamMemberReq,
    TeamCreateReq,
    TeamModel,
)
from app.schemas.user import UserModel


async def create_team_service(
    db: AsyncDatabase, team_create: TeamCreateReq, creator_id: str
) -> TeamModel:

    team_in_db_dict = await db_create_team(db, team_create, creator_id)

    return TeamModel(
        id=team_in_db_dict["_id"],
        name=team_in_db_dict["name"],
        member_ids=team_in_db_dict["member_ids"],
        exec_member_ids=team_in_db_dict["exec_member_ids"],
        project_ids=team_in_db_dict["project_ids"],
    )


async def get_team_service(
    team_id: str, current_user: UserModel, db: AsyncDatabase
) -> GetTeamResponse:
    existing_team = await db_get_team_by_id(db, team_id)
    if not existing_team:
        raise HTTPException(
            status_code=404, detail=f"Team does not exist: team_id={team_id}"
        )

    user_in_team = current_user.id in existing_team["member_ids"]
    if not user_in_team:
        raise HTTPException(
            status_code=403,
            detail=f"User is not a member of the team: user_id={current_user.id}, team_id={team_id}",
        )

    return GetTeamResponse(
        team=TeamModel(
            id=existing_team["_id"],
            name=existing_team["name"],
            member_ids=existing_team["member_ids"],
            exec_member_ids=existing_team["exec_member_ids"],
        )
    )


async def join_team_service(db: AsyncDatabase, team_id: str, user_id: str) -> None:
    existing_team = await db_get_team_by_id(db, team_id)
    if not existing_team:
        raise ValueError(f"Team with ID '{team_id}' does not exist")

    user_already_in_team = user_id in existing_team["member_ids"]
    if user_already_in_team:
        raise ValueError(f"User with ID '{user_id}' is already in team '{team_id}'")

    await db_join_team(db, team_id, user_id)


async def promote_team_member_service(
    db: AsyncDatabase, team_id: str, promote_member_id: str, caller_id: str
) -> None:
    existing_team = await db_get_team_by_id(db, team_id)
    if not existing_team:
        raise ValueError(f"Team with ID '{team_id}' does not exist")

    if promote_member_id not in existing_team["member_ids"]:
        raise ValueError(
            f"Member with ID '{promote_member_id}' is not in team '{team_id}'"
        )

    if caller_id not in existing_team["exec_member_ids"]:
        raise ValueError(
            f"User with ID '{caller_id}' does not have permission to promote members in team '{team_id}'"
        )

    await db_promote_team_member(db, team_id, promote_member_id)


async def leave_team_service(db: AsyncDatabase, team_id: str, user_id: str) -> None:
    existing_team = await db_get_team_by_id(db, team_id)
    if not existing_team:
        raise ValueError(f"Team with ID '{team_id}' does not exist")

    user_in_team = user_id in existing_team["member_ids"]
    if not user_in_team:
        raise ValueError(f"User with ID '{user_id}' is not in team '{team_id}'")

    if (
        user_id in existing_team["exec_member_ids"]
        and len(existing_team["exec_member_ids"]) == 1
    ):
        raise ValueError(
            f"User with ID '{user_id}' is the last executive member and cannot leave the team '{team_id}'"
        )

    await db_leave_team(db, team_id, user_id)


async def kick_team_member_service(
    db: AsyncDatabase, team_id: str, kick_member_id: str, caller_id: str
) -> None:
    existing_team = await db_get_team_by_id(db, team_id)
    if not existing_team:
        raise ValueError(f"Team with ID '{team_id}' does not exist")

    if kick_member_id not in existing_team["member_ids"]:
        raise ValueError(
            f"Member with ID '{kick_member_id}' is not in team '{team_id}'"
        )

    if kick_member_id in existing_team["exec_member_ids"]:
        raise ValueError(
            f"Member with ID '{kick_member_id}' is an executive and cannot be kicked"
        )

    if caller_id not in existing_team["exec_member_ids"]:
        raise ValueError(
            f"User with ID '{caller_id}' does not have permission to kick members from team '{team_id}'"
        )

    await db_kick_team_member(db, team_id, kick_member_id, caller_id)


async def create_project_service(
    team_id: str, create_project_request: CreateProjectRequest, db: AsyncDatabase
) -> CreateProjectResponse:

    project_in_db_dict = await db_create_project(team_id, create_project_request, db)

    return CreateProjectResponse(
        project=Project(
            id=project_in_db_dict["_id"],
            name=project_in_db_dict["name"],
            description=project_in_db_dict["description"],
            todo_statuses=project_in_db_dict["todo_statuses"],
            todo_ids=project_in_db_dict["todo_ids"],
        )
    )
