from fastapi import APIRouter, Depends
from pymongo.asynchronous.database import AsyncDatabase
from typing import Annotated

from app.db.client import get_db

from app.schemas.team import TeamCreateReq, TeamModel
from app.schemas.user import UserModel
from app.service.team import create_team_service
from app.api.auth import get_current_user


router = APIRouter()


@router.post("/create_team", response_model=TeamModel)
async def create_team(
    team_create: TeamCreateReq,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncDatabase = Depends(get_db),
) -> TeamModel:
    return await create_team_service(db, team_create, current_user.id)
