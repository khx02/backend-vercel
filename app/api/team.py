from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.asynchronous.database import AsyncDatabase

from app.db.client import get_db

from app.schemas.team import TeamCreateReq, TeamModel
from app.schemas.user import UserModel
from app.service.team import create_team_service, join_team_service, leave_team_service
from app.api.auth import get_current_user


router = APIRouter()


# TODO: Returning the object ID and using it to join teams is not the most user-friendly
# May be worth considering using shortened team ids or other identifiers instead
# Team name has been made unique, so we may be able to use it for joining
@router.post("/create_team", response_model=TeamModel)
async def create_team(
    team_create: TeamCreateReq,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncDatabase = Depends(get_db),
) -> TeamModel:
    try:
        return await create_team_service(db, team_create, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create team",
        )


@router.post("/join_team/{team_id}")
async def join_team(
    team_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncDatabase = Depends(get_db),
) -> None:
    try:
        await join_team_service(db, team_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to join team",
        )


@router.post("/leave_team/{team_id}")
async def leave_team(
    team_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: AsyncDatabase = Depends(get_db),
) -> None:
    try:
        await leave_team_service(db, team_id, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to leave team",
        )
