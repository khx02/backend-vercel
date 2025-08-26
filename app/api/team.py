from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.asynchronous.database import AsyncDatabase

from app.api.auth import get_current_user
from app.db.client import get_db
from app.schemas.team import (
    CreateProjectRequest,
    CreateProjectResponse,
    CreateTeamRequest,
    CreateTeamResponse,
    GetTeamResponse,
    JoinTeamResponse,
    KickTeamMemberRequest,
    KickTeamMemberResponse,
    LeaveTeamResponse,
    PromoteTeamMemberRequest,
    PromoteTeamMemberResponse,
    TeamModel,
)
from app.schemas.user import UserModel
from app.service.team import (
    create_project_service,
    create_team_service,
    get_team_service,
    join_team_service,
    kick_team_member_service,
    leave_team_service,
    promote_team_member_service,
)

router = APIRouter()


@router.post("/create-team", response_model=TeamModel)
async def create_team(
    create_team_request: CreateTeamRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncDatabase = Depends(get_db),
) -> CreateTeamResponse:
    return await create_team_service(current_user.id, create_team_request.name, db)


@router.post("/join-team/{team_id}")
async def join_team(
    team_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncDatabase = Depends(get_db),
) -> JoinTeamResponse:
    return await join_team_service(team_id, current_user.id, db)


@router.get("/get-team/{team_id}")
async def get_team(
    team_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncDatabase = Depends(get_db),
) -> GetTeamResponse:
    return await get_team_service(team_id, current_user, db)


@router.post("/promote-team-member/{team_id}")
async def promote_team_member(
    team_id: str,
    promote_team_member_request: PromoteTeamMemberRequest,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncDatabase = Depends(get_db),
) -> PromoteTeamMemberResponse:
    return await promote_team_member_service(
        team_id, promote_team_member_request.member_id, current_user.id, db
    )


@router.post("/leave-team/{team_id}")
async def leave_team(
    team_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncDatabase = Depends(get_db),
) -> LeaveTeamResponse:
    return await leave_team_service(team_id, current_user.id, db)


@router.post("/kick-team-member/{team_id}")
async def kick_team_member(
    team_id: str,
    kick_team_member: KickTeamMemberRequest,
    current_user: UserModel = Depends(get_current_user),
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
