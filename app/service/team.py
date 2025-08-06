from app.schemas.team import TeamCreateReq, TeamModel
from app.db.team import create_team as db_create_team
from pymongo.asynchronous.database import AsyncDatabase


async def create_team_service(
    db: AsyncDatabase, team_create: TeamCreateReq, creator_id: str
) -> TeamModel:
    team_in_db_dict = await db_create_team(db, team_create, creator_id)

    return TeamModel(
        id=team_in_db_dict["_id"],
        name=team_in_db_dict["name"],
        member_ids=team_in_db_dict["member_ids"],
    )
