from fastapi import HTTPException
from pymongo.asynchronous.database import AsyncDatabase

from app.db.team import (
    db_create_event_for_team,
    db_create_team,
    db_join_team,
    db_create_project,
    db_get_team_by_id,
    db_promote_team_member,
    db_leave_team,
    db_kick_team_member,
)
from app.schemas.event import Event
from app.schemas.project import Project
from app.schemas.team import (
    CreateEventRequest,
    CreateProjectRequest,
    CreateProjectResponse,
    CreateTeamResponse,
    GetTeamResponse,
    JoinTeamResponse,
    KickTeamMemberResponse,
    LeaveTeamResponse,
    PromoteTeamMemberResponse,
    TeamModel,
)
from app.schemas.user import UserModel


async def create_team_service(
    creator_id: str, team_name: str, db: AsyncDatabase
) -> CreateTeamResponse:

    team_in_db_dict = await db_create_team(creator_id, team_name, db)

    return CreateTeamResponse(
        team=TeamModel(
            id=team_in_db_dict["_id"],
            name=team_in_db_dict["name"],
            member_ids=team_in_db_dict["member_ids"],
            exec_member_ids=team_in_db_dict["exec_member_ids"],
            project_ids=team_in_db_dict["project_ids"],
            event_ids=team_in_db_dict["event_ids"],
        )
    )


async def join_team_service(
    team_id: str, user_id: str, db: AsyncDatabase
) -> JoinTeamResponse:
    existing_team = await db_get_team_by_id(team_id, db)
    if not existing_team:
        raise HTTPException(
            status_code=404, detail=f"Team does not exist: team_id={team_id}"
        )

    user_already_in_team = user_id in existing_team["member_ids"]
    if user_already_in_team:
        raise HTTPException(
            status_code=400,
            detail=f"User is already in the team: user_id={user_id}, team_id={team_id}",
        )

    await db_join_team(team_id, user_id, db)

    return JoinTeamResponse()


async def get_team_service(
    team_id: str, current_user: UserModel, db: AsyncDatabase
) -> GetTeamResponse:
    existing_team = await db_get_team_by_id(team_id, db)
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
            project_ids=existing_team["project_ids"],
            event_ids=existing_team["event_ids"],
        )
    )


async def promote_team_member_service(
    team_id: str, promote_member_id: str, caller_id: str, db: AsyncDatabase
) -> PromoteTeamMemberResponse:
    existing_team = await db_get_team_by_id(team_id, db)
    if not existing_team:
        raise HTTPException(
            status_code=404, detail=f"Team does not exist: team_id={team_id}"
        )

    if promote_member_id not in existing_team["member_ids"]:
        raise HTTPException(
            status_code=403,
            detail=f"Member is not in the team: member_id={promote_member_id}, team_id={team_id}",
        )

    if caller_id not in existing_team["exec_member_ids"]:
        raise HTTPException(
            status_code=403,
            detail=f"User does not have permission to promote members in team: user_id={caller_id}, team_id={team_id}",
        )

    await db_promote_team_member(team_id, promote_member_id, db)

    return PromoteTeamMemberResponse()


async def leave_team_service(
    team_id: str, user_id: str, db: AsyncDatabase
) -> LeaveTeamResponse:
    existing_team = await db_get_team_by_id(team_id, db)
    if not existing_team:
        raise HTTPException(
            status_code=404, detail=f"Team does not exist: team_id={team_id}"
        )

    user_in_team = user_id in existing_team["member_ids"]
    if not user_in_team:
        raise HTTPException(
            status_code=403,
            detail=f"User is not a member of the team: user_id={user_id}, team_id={team_id}",
        )

    if (
        user_id in existing_team["exec_member_ids"]
        and len(existing_team["exec_member_ids"]) == 1
    ):
        raise HTTPException(
            status_code=403,
            detail=f"User is the last executive member and cannot leave the team: user_id={user_id}, team_id={team_id}",
        )

    await db_leave_team(team_id, user_id, db)

    return LeaveTeamResponse()


async def kick_team_member_service(
    team_id: str, kick_member_id: str, caller_id: str, db: AsyncDatabase
) -> KickTeamMemberResponse:
    existing_team = await db_get_team_by_id(team_id, db)
    if not existing_team:
        raise HTTPException(
            status_code=404, detail=f"Team does not exist: team_id={team_id}"
        )

    if kick_member_id not in existing_team["member_ids"]:
        raise HTTPException(
            status_code=403,
            detail=f"Member is not in the team: member_id={kick_member_id}, team_id={team_id}",
        )

    if kick_member_id in existing_team["exec_member_ids"]:
        raise HTTPException(
            status_code=403,
            detail=f"Member is an executive and cannot be kicked: member_id={kick_member_id}, team_id={team_id}",
        )

    if caller_id not in existing_team["exec_member_ids"]:
        raise HTTPException(
            status_code=403,
            detail=f"User does not have permission to kick members from team: user_id={caller_id}, team_id={team_id}",
        )

    await db_kick_team_member(team_id, kick_member_id, db)

    return KickTeamMemberResponse()


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


async def create_event_for_team_service(
    team_id: str, create_event_request: CreateEventRequest, db: AsyncDatabase
) -> Event:

    event_in_db_dict = await db_create_event_for_team(team_id, create_event_request, db)

    return Event(
        id=event_in_db_dict["_id"],
        name=event_in_db_dict["name"],
        description=event_in_db_dict["description"],
    )
