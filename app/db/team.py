from typing import Any, Dict, List

from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from app.core.constants import PROJECTS_COLLECTION, TEAMS_COLLECTION
from app.schemas.project import TodoStatus
from app.schemas.team import CreateProjectRequest, TeamCreateReq


def stringify_team_dict(team_dict: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "_id": str(team_dict["_id"]),
        "name": team_dict["name"],
        "member_ids": [str(member_id) for member_id in team_dict.get("member_ids", [])],
        "exec_member_ids": [
            str(member_id) for member_id in team_dict.get("exec_member_ids", [])
        ],
    }

    team_dict["_id"] = str(team_dict["_id"])
    return team_dict


async def create_team(
    db: AsyncDatabase, team_req: TeamCreateReq, creator_id: str
) -> Dict[str, Any]:
    team_dict = {
        "name": team_req.name,
        "member_ids": [ObjectId(creator_id)],
        "exec_member_ids": [ObjectId(creator_id)],
    }

    result = await db[TEAMS_COLLECTION].insert_one(team_dict)
    team_dict["_id"] = result.inserted_id

    team_dict = stringify_team_dict(team_dict)
    return team_dict


async def join_team(db: AsyncDatabase, team_id: str, user_id: str) -> None:
    try:
        await db[TEAMS_COLLECTION].update_one(
            {"_id": ObjectId(team_id)}, {"$addToSet": {"member_ids": ObjectId(user_id)}}
        )
    except Exception as e:
        raise ValueError(f"Failed to add user to team: {str(e)}")


async def get_team_by_name(db: AsyncDatabase, team_name: str) -> Dict[str, Any] | None:
    try:
        team_dict = await db[TEAMS_COLLECTION].find_one({"name": team_name})
        if team_dict:
            return stringify_team_dict(team_dict)
        return None
    except Exception as e:
        return None


async def get_team_by_id(db: AsyncDatabase, team_id: str) -> Dict[str, Any] | None:
    try:
        team_dict = await db[TEAMS_COLLECTION].find_one({"_id": ObjectId(team_id)})
        if team_dict:
            return stringify_team_dict(team_dict)
        return None
    except Exception as e:
        return None


async def get_team_members(db: AsyncDatabase, team_id: str) -> List[str] | None:
    try:
        team_dict = await db[TEAMS_COLLECTION].find_one({"_id": ObjectId(team_id)})
        if team_dict:
            team_dict = stringify_team_dict(team_dict)
            return team_dict["member_ids"]
        return None
    except Exception as e:
        return None


async def add_kanban_to_team(db: AsyncDatabase, team_id: str, kanban_id: str) -> None:
    try:
        await db[TEAMS_COLLECTION].update_one(
            {"_id": ObjectId(team_id)},
            {"$addToSet": {"kanban_ids": ObjectId(kanban_id)}},
        )
    except Exception as e:
        raise ValueError(f"Failed to add kanban to team: {str(e)}")


async def promote_team_member(db: AsyncDatabase, team_id: str, member_id: str) -> None:
    try:
        await db[TEAMS_COLLECTION].update_one(
            {"_id": ObjectId(team_id)},
            {"$addToSet": {"exec_member_ids": ObjectId(member_id)}},
        )
    except Exception as e:
        raise ValueError(f"Failed to promote team member: {str(e)}")


async def leave_team(db: AsyncDatabase, team_id: str, user_id: str) -> None:
    try:
        await db[TEAMS_COLLECTION].update_one(
            {"_id": ObjectId(team_id)},
            {
                "$pull": {
                    "member_ids": ObjectId(user_id),
                    "exec_member_ids": ObjectId(user_id),
                }
            },
        )
    except Exception as e:
        raise ValueError(f"Failed to remove user from team: {str(e)}")


async def kick_team_member(
    db: AsyncDatabase, team_id: str, kick_member_id: str, caller_id: str
) -> None:
    try:
        await db[TEAMS_COLLECTION].update_one(
            {"_id": ObjectId(team_id)},
            {"$pull": {"member_ids": ObjectId(kick_member_id)}},
        )
    except Exception as e:
        raise ValueError(f"Failed to remove user from team: {str(e)}")


async def db_create_project(
    team_id: str, create_project_request: CreateProjectRequest, db: AsyncDatabase
) -> Dict[str, Any]:

    project_dict = {
        "name": create_project_request.name,
        "description": create_project_request.description,
        "todo_statuses": [
            {"id": str(ObjectId()), "name": "To Do"},
            {"id": str(ObjectId()), "name": "In Progress"},
            {"id": str(ObjectId()), "name": "Done"},
        ],
        "todo_ids": [],
    }

    result = await db[PROJECTS_COLLECTION].insert_one(project_dict)

    project_dict["_id"] = str(result.inserted_id)
    await db[TEAMS_COLLECTION].update_one(
        {"_id": ObjectId(team_id)},
        {"$addToSet": {"project_ids": project_dict["_id"]}},
    )

    return project_dict
