"""
from pymongo.asynchronous.database import AsyncDatabase
from app.schemas.team import TeamCreateReq, TeamJoinReq
from typing import Dict, Any, List

from bson import ObjectId

from app.core.constants import TEAMS_COLLECTION


async def create_team(
    db: AsyncDatabase, team_req: TeamCreateReq, creator_id: str
) -> Dict[str, Any]:
    team_dict = {
        "name": team_req.name,
        "member_ids": [creator_id],
        "exec_member_ids": [creator_id],
    }

    result = await db[TEAMS_COLLECTION].insert_one(team_dict)

    team_dict["_id"] = str(result.inserted_id)
    return team_dict


async def join_team(db: AsyncDatabase, team_join: TeamJoinReq, user_id: str) -> None:
    await db[TEAMS_COLLECTION].update_one(
        {"_id": ObjectId(team_join.team_id)}, {"$addToSet": {"member_ids": user_id}}
    )


async def get_team_by_name(db: AsyncDatabase, team_name: str) -> Dict[str, Any] | None:
    try:
        team_dict = await db[TEAMS_COLLECTION].find_one({"name": team_name})
        if team_dict:
            team_dict["_id"] = str(team_dict["_id"])
            return team_dict
        return None
    except Exception as e:
        return None


async def get_team_by_id(db: AsyncDatabase, team_id: str) -> Dict[str, Any] | None:
    try:
        team_dict = await db[TEAMS_COLLECTION].find_one({"_id": ObjectId(team_id)})
        if team_dict:
            team_dict["_id"] = str(team_dict["_id"])
            return team_dict
        return None
    except Exception as e:
        return None


async def get_team_members(db: AsyncDatabase, team_id: str) -> List[str] | None:
    try:
        team_dict = await db[TEAMS_COLLECTION].find_one({"_id": ObjectId(team_id)})
        if team_dict:
            return [str(member_id) for member_id in team_dict.get("member_ids", [])]
        return None
    except Exception as e:
        return None

"""

from pymongo.asynchronous.database import AsyncDatabase
from app.schemas.kanban import KanbanCreateReq

from typing import Dict, Any

from app.core.constants import KANBANS_COLLECTION


async def create_kanban(
    db: AsyncDatabase, kanban_create: KanbanCreateReq
) -> Dict[str, Any] | None:

    kanban_dict = {
        "name": kanban_create.name,
    }

    result = await db[KANBANS_COLLECTION].insert_one(kanban_dict)

    kanban_dict["_id"] = str(result.inserted_id)
    return kanban_dict
