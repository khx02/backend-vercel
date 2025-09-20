from fastapi import Depends, HTTPException
from app.api.auth import get_current_user_info
from app.db.client import get_db
from app.schemas.user import UserModel

from pymongo.asynchronous.database import AsyncDatabase

from app.service.user import get_current_user_teams_service


async def require_standard_project_access(
    project_id: str,
    current_user: UserModel = Depends(get_current_user_info),
    db: AsyncDatabase = Depends(get_db),
) -> None:
    user_teams = (await get_current_user_teams_service(current_user.id, db)).teams

    found_access = False
    for team in user_teams:
        if project_id in team.project_ids:
            found_access = True
            break

    if not found_access:
        raise HTTPException(
            status_code=403,
            detail=f"Not enough permissions to perform operation on project: project_id={project_id}",
        )


async def require_executive_project_access(
    project_id: str,
    current_user: UserModel = Depends(get_current_user_info),
    db: AsyncDatabase = Depends(get_db),
) -> None:
    user_teams = (await get_current_user_teams_service(current_user.id, db)).teams

    found_access = False
    for team in user_teams:
        if project_id in team.project_ids and current_user.id in team.exec_member_ids:
            found_access = True
            break

    if not found_access:
        raise HTTPException(
            status_code=403,
            detail=f"Not enough permissions to perform operation on project: project_id={project_id}",
        )
