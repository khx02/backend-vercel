from app.schemas.team import TeamCreateReq, TeamModel, KickTeamMemberReq
from app.db.team import (
    create_team as db_create_team,
    join_team as db_join_team,
    get_team_by_name as db_get_team_by_name,
    get_team_by_id as db_get_team_by_id,
    get_team_members as db_get_team_members,
    leave_team as db_leave_team,
    kick_team_member as db_kick_team_member,
)
from pymongo.asynchronous.database import AsyncDatabase


async def create_team_service(
    db: AsyncDatabase, team_create: TeamCreateReq, creator_id: str
) -> TeamModel:

    existing_team = await db_get_team_by_name(db, team_create.name)
    if existing_team:
        raise ValueError(f"Team with name '{team_create.name}' already exists")

    team_in_db_dict = await db_create_team(db, team_create, creator_id)

    return TeamModel(
        id=team_in_db_dict["_id"],
        name=team_in_db_dict["name"],
        member_ids=team_in_db_dict["member_ids"],
        exec_member_ids=team_in_db_dict["exec_member_ids"],
    )


async def join_team_service(db: AsyncDatabase, team_id: str, user_id: str) -> None:
    existing_team = await db_get_team_by_id(db, team_id)
    if not existing_team:
        raise ValueError(f"Team with ID '{team_id}' does not exist")

    user_already_in_team = user_id in await db_get_team_members(db, team_id)
    if user_already_in_team:
        raise ValueError(f"User with ID '{user_id}' is already in team '{team_id}'")

    await db_join_team(db, team_id, user_id)


async def leave_team_service(db: AsyncDatabase, team_id: str, user_id: str) -> None:
    existing_team = await db_get_team_by_id(db, team_id)
    if not existing_team:
        raise ValueError(f"Team with ID '{team_id}' does not exist")

    user_in_team = user_id in await db_get_team_members(db, team_id)
    if not user_in_team:
        raise ValueError(f"User with ID '{user_id}' is not in team '{team_id}'")

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

    if caller_id not in existing_team["exec_member_ids"]:
        raise ValueError(
            f"User with ID '{caller_id}' does not have permission to kick members from team '{team_id}'"
        )

    await db_kick_team_member(db, team_id, kick_member_id, caller_id)
