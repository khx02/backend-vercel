from fastapi import APIRouter, Depends
from pymongo.asynchronous.database import AsyncDatabase

from app.db.client import get_db

from app.schemas.team import TeamCreateReq, TeamModel, TeamJoinReq
from app.schemas.user import UserModel
from app.service.team import create_team_service, join_team_service
from app.api.auth import get_current_user


router = APIRouter()


# TODO: Returning the object ID and using it to join teams is not the most user-friendly
# May be worth considering using shortened team ids or other identifiers instead
@router.post("/create_team", response_model=TeamModel)
async def create_team(
    team_create: TeamCreateReq,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncDatabase = Depends(get_db),
) -> TeamModel:
    return await create_team_service(db, team_create, current_user.id)


@router.post("/join_team")
async def join_team(
    team_join: TeamJoinReq,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncDatabase = Depends(get_db),
) -> None:
    await join_team_service(db, team_join, current_user.id)
