from fastapi import APIRouter, Depends
from pymongo.asynchronous.database import AsyncDatabase

from app.api.auth import get_current_user_info
from app.db.client import get_db
from app.schemas.team import (
    CreateEventRequest,
    CreateEventResponse,
    CreateProjectRequest,
    CreateProjectResponse,
    CreateTeamRequest,
    CreateTeamResponse,
    DeleteEventRequest,
    DeleteEventResponse,
    DeleteProjectRequest,
    DeleteProjectResponse,
    DeleteTeamResponse,
    GetTeamEventsResponse,
    GetTeamResponse,
    JoinTeamByShortIdResponse,
    JoinTeamResponse,
    KickTeamMemberRequest,
    KickTeamMemberResponse,
    LeaveTeamResponse,
    PromoteTeamMemberRequest,
    PromoteTeamMemberResponse,
)
from app.schemas.user import UserModel
from app.service.team import (
    create_event_for_team_service,
    create_project_service,
    create_team_service,
    delete_event_service,
    delete_project_service,
    delete_team_service,
    get_team_events_service,
    get_team_service,
    join_team_by_short_id_service,
    join_team_service,
    kick_team_member_service,
    leave_team_service,
    promote_team_member_service,
)

router = APIRouter()


@router.post("/create-team")
async def create_team(
    create_team_request: CreateTeamRequest,
    current_user: UserModel = Depends(get_current_user_info),
    db: AsyncDatabase = Depends(get_db),
) -> CreateTeamResponse:
    return await create_team_service(current_user.id, create_team_request.name, db)


@router.post("/join-team/{team_id}")
async def join_team(
    team_id: str,
    current_user: UserModel = Depends(get_current_user_info),
    db: AsyncDatabase = Depends(get_db),
) -> JoinTeamResponse:
    return await join_team_service(team_id, current_user.id, db)


@router.post("/join-team-by-short-id/{team_short_id}")
async def join_team_by_short_id(
    team_short_id: str,
    current_user: UserModel = Depends(get_current_user_info),
    db: AsyncDatabase = Depends(get_db),
) -> JoinTeamByShortIdResponse:
    await join_team_by_short_id_service(team_short_id, current_user.id, db)

    return JoinTeamByShortIdResponse()


@router.get("/get-team/{team_id}")
async def get_team(
    team_id: str,
    current_user: UserModel = Depends(get_current_user_info),
    db: AsyncDatabase = Depends(get_db),
) -> GetTeamResponse:
    return await get_team_service(team_id, current_user, db)


@router.post("/promote-team-member/{team_id}")
async def promote_team_member(
    team_id: str,
    promote_team_member_request: PromoteTeamMemberRequest,
    current_user: UserModel = Depends(get_current_user_info),
    db: AsyncDatabase = Depends(get_db),
) -> PromoteTeamMemberResponse:
    return await promote_team_member_service(
        team_id, promote_team_member_request.member_id, current_user.id, db
    )


@router.post("/leave-team/{team_id}")
async def leave_team(
    team_id: str,
    current_user: UserModel = Depends(get_current_user_info),
    db: AsyncDatabase = Depends(get_db),
) -> LeaveTeamResponse:
    return await leave_team_service(team_id, current_user.id, db)


@router.post("/delete-team/{team_id}")
async def delete_team(
    team_id: str,
    current_user: UserModel = Depends(get_current_user_info),
    db: AsyncDatabase = Depends(get_db),
) -> DeleteTeamResponse:
    await delete_team_service(team_id, current_user.id, db)

    return DeleteTeamResponse()


@router.post("/kick-team-member/{team_id}")
async def kick_team_member(
    team_id: str,
    kick_team_member: KickTeamMemberRequest,
    current_user: UserModel = Depends(get_current_user_info),
    db: AsyncDatabase = Depends(get_db),
) -> KickTeamMemberResponse:
    return await kick_team_member_service(
        team_id, kick_team_member.member_id, current_user.id, db
    )


@router.post("/create-project/{team_id}")
async def create_project(
    team_id: str,
    create_project_request: CreateProjectRequest,
    db: AsyncDatabase = Depends(get_db),
) -> CreateProjectResponse:
    return await create_project_service(team_id, create_project_request, db)


@router.delete("/delete-project/{team_id}")
async def delete_project(
    team_id: str,
    delete_project_request: DeleteProjectRequest,
    current_user: UserModel = Depends(get_current_user_info),
    db: AsyncDatabase = Depends(get_db),
) -> DeleteProjectResponse:

    await delete_project_service(
        team_id, delete_project_request.project_id, current_user.id, db
    )

    return DeleteProjectResponse()


@router.post("/create-event/{team_id}")
async def create_event(
    team_id: str,
    create_event_request: CreateEventRequest,
    db: AsyncDatabase = Depends(get_db),
) -> CreateEventResponse:
    return CreateEventResponse(
        event=await create_event_for_team_service(team_id, create_event_request, db)
    )


@router.post("/delete-event/{team_id}")
async def delete_event(
    team_id: str,
    delete_event_request: DeleteEventRequest,
    current_user: UserModel = Depends(get_current_user_info),
    db: AsyncDatabase = Depends(get_db),
) -> DeleteEventResponse:
    await delete_event_service(
        team_id, delete_event_request.event_id, current_user.id, db
    )
    return DeleteEventResponse()


@router.post("/get-team-events/{team_id}")
async def get_team_events(
    team_id: str,
    current_user: UserModel = Depends(get_current_user_info),
    db: AsyncDatabase = Depends(get_db),
) -> GetTeamEventsResponse:

    return GetTeamEventsResponse(
        events=await get_team_events_service(team_id, current_user.id, db)
    )
