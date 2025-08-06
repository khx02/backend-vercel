from app.schemas.team import TeamCreateReq, TeamModel, TeamJoinReq
from app.db.team import (
    create_team as db_create_team,
    join_team as db_join_team,
    get_team_by_name as db_get_team_by_name,
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


# TODO: Handle case where team does not exist or user is already in the team
# Case where user is already on team is handled by MongoDB addToSet, but might be good to handle explicitly
async def join_team_service(
    db: AsyncDatabase, team_join: TeamJoinReq, user_id: str
) -> None:
    await db_join_team(db, team_join, user_id)
