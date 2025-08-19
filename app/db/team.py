from typing import Any, Dict, List

from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from app.core.constants import TEAMS_COLLECTION
from app.schemas.team import TeamCreateReq


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


async def join_team(db: AsyncDatabase, team_id: str, user_id: str) -> None:
    try:
        await db[TEAMS_COLLECTION].update_one(
            {"_id": ObjectId(team_id)}, {"$addToSet": {"member_ids": user_id}}
        )
    except Exception as e:
        raise ValueError(f"Failed to add user to team: {str(e)}")


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


async def add_kanban_to_team(db: AsyncDatabase, team_id: str, kanban_id: str) -> None:
    try:
        await db[TEAMS_COLLECTION].update_one(
            {"_id": ObjectId(team_id)}, {"$addToSet": {"kanban_ids": kanban_id}}
        )
    except Exception as e:
        raise ValueError(f"Failed to add kanban to team: {str(e)}")


async def promote_team_member(db: AsyncDatabase, team_id: str, member_id: str) -> None:
    try:
        await db[TEAMS_COLLECTION].update_one(
            {"_id": ObjectId(team_id)},
            {"$addToSet": {"exec_member_ids": member_id}},
        )
    except Exception as e:
        raise ValueError(f"Failed to promote team member: {str(e)}")


async def leave_team(db: AsyncDatabase, team_id: str, user_id: str) -> None:
    try:
        await db[TEAMS_COLLECTION].update_one(
            {"_id": ObjectId(team_id)},
            {"$pull": {"member_ids": user_id, "exec_member_ids": user_id}},
        )
    except Exception as e:
        raise ValueError(f"Failed to remove user from team: {str(e)}")


async def kick_team_member(
    db: AsyncDatabase, team_id: str, kick_member_id: str, caller_id: str
) -> None:
    try:
        await db[TEAMS_COLLECTION].update_one(
            {"_id": ObjectId(team_id)},
            {"$pull": {"member_ids": kick_member_id}},
        )
    except Exception as e:
        raise ValueError(f"Failed to remove user from team: {str(e)}")
