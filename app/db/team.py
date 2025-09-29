from typing import Any, Dict, List

from bson import ObjectId
from pymongo.asynchronous.database import AsyncDatabase

from app.core.common import stringify_object_ids
from app.core.constants import EVENTS_COLLECTION, PROJECTS_COLLECTION, TEAMS_COLLECTION
from app.schemas.team import CreateEventRequest, CreateProjectRequest


async def db_create_team(
    creator_id: str, short_id: str, team_name: str, db: AsyncDatabase
) -> Dict[str, Any]:
    team_dict = {
        "short_id": short_id,
        "name": team_name,
        "member_ids": [ObjectId(creator_id)],
        "exec_member_ids": [ObjectId(creator_id)],
        "project_ids": [],
        "event_ids": [],
    }

    result = await db[TEAMS_COLLECTION].insert_one(team_dict)
    team_dict["_id"] = result.inserted_id

    return stringify_object_ids(team_dict)


async def db_join_team(team_id: str, user_id: str, db: AsyncDatabase) -> None:
    await db[TEAMS_COLLECTION].update_one(
        {"_id": ObjectId(team_id)}, {"$addToSet": {"member_ids": ObjectId(user_id)}}
    )


async def db_get_team_by_id(team_id: str, db: AsyncDatabase) -> Dict[str, Any]:
    team_dict = await db[TEAMS_COLLECTION].find_one({"_id": ObjectId(team_id)})
    return stringify_object_ids(team_dict)


async def db_get_team_id_by_short_id(short_id: str, db: AsyncDatabase) -> str | None:
    team_dict = await db[TEAMS_COLLECTION].find_one({"short_id": short_id})
    return str(team_dict["_id"]) if team_dict else None


async def db_get_team_by_short_id(
    short_id: str, db: AsyncDatabase
) -> Dict[str, Any] | None:
    team_dict = await db[TEAMS_COLLECTION].find_one({"short_id": short_id})
    return stringify_object_ids(team_dict) if team_dict else None


async def db_promote_team_member(
    team_id: str, promote_member_id: str, db: AsyncDatabase
) -> None:
    await db[TEAMS_COLLECTION].update_one(
        {"_id": ObjectId(team_id)},
        {"$addToSet": {"exec_member_ids": ObjectId(promote_member_id)}},
    )


async def db_leave_team(team_id: str, user_id: str, db: AsyncDatabase) -> None:
    await db[TEAMS_COLLECTION].update_one(
        {"_id": ObjectId(team_id)},
        {
            "$pull": {
                "member_ids": ObjectId(user_id),
                "exec_member_ids": ObjectId(user_id),
            }
        },
    )


async def db_delete_team(team_id: str, db: AsyncDatabase) -> None:
    await db[TEAMS_COLLECTION].delete_one({"_id": ObjectId(team_id)})


async def db_kick_team_member(
    team_id: str, kick_member_id: str, db: AsyncDatabase
) -> None:
    await db[TEAMS_COLLECTION].update_one(
        {"_id": ObjectId(team_id)},
        {"$pull": {"member_ids": ObjectId(kick_member_id)}},
    )


async def db_create_project(
    team_id: str, create_project_request: CreateProjectRequest, db: AsyncDatabase
) -> Dict[str, Any]:

    project_dict = {
        "name": create_project_request.name,
        "description": create_project_request.description,
        "todo_statuses": [
            {"id": ObjectId(), "name": "To Do", "color": "#6B7280"},
            {"id": ObjectId(), "name": "In Progress", "color": "#F59E0B"},
            {"id": ObjectId(), "name": "Done", "color": "#10B981"},
        ],
        "todo_ids": [],
        "budget_available": 0.0,
        "budget_spent": 0.0,
    }

    result = await db[PROJECTS_COLLECTION].insert_one(project_dict)

    project_dict["_id"] = result.inserted_id
    await db[TEAMS_COLLECTION].update_one(
        {"_id": ObjectId(team_id)},
        {"$addToSet": {"project_ids": project_dict["_id"]}},
    )

    return stringify_object_ids(project_dict)


async def db_get_project_by_id(
    project_id: str, db: AsyncDatabase
) -> Dict[str, Any] | None:
    project_dict = await db[PROJECTS_COLLECTION].find_one({"_id": ObjectId(project_id)})
    return stringify_object_ids(project_dict)


async def db_get_project_ids_by_team_id(
    team_id: str, db: AsyncDatabase
) -> List[Dict[str, Any]]:
    try:
        team = await db[TEAMS_COLLECTION].find_one({"_id": ObjectId(team_id)})
        if not team:
            return []

        return team.get("project_ids", [])
    except Exception:
        return []


async def db_delete_project(project_id: str, db: AsyncDatabase) -> None:
    await db[PROJECTS_COLLECTION].delete_one({"_id": ObjectId(project_id)})
    await db[TEAMS_COLLECTION].update_many(
        {"project_ids": ObjectId(project_id)},
        {"$pull": {"project_ids": ObjectId(project_id)}},
    )


async def db_create_event_for_team(
    team_id: str, create_event_request: CreateEventRequest, db: AsyncDatabase
) -> Dict[str, Any]:
    event_dict = {
        "name": create_event_request.name,
        "description": create_event_request.description,
        "start": create_event_request.start,
        "end": create_event_request.end,
        "colour": create_event_request.colour,
        "location": create_event_request.location,
        "rsvp_ids": [],
    }

    result = await db[EVENTS_COLLECTION].insert_one(event_dict)
    event_dict["_id"] = result.inserted_id

    await db[TEAMS_COLLECTION].update_one(
        {"_id": ObjectId(team_id)},
        {"$addToSet": {"event_ids": event_dict["_id"]}},
    )

    return stringify_object_ids(event_dict)


async def db_get_event_by_id(event_id: str, db: AsyncDatabase) -> Dict[str, Any] | None:
    event_dict = await db[EVENTS_COLLECTION].find_one({"_id": ObjectId(event_id)})
    return stringify_object_ids(event_dict)


async def db_delete_event(team_id: str, event_id: str, db: AsyncDatabase) -> None:
    await db[EVENTS_COLLECTION].delete_one({"_id": ObjectId(event_id)})
    await db[TEAMS_COLLECTION].update_one(
        {"_id": ObjectId(team_id)},
        {"$pull": {"event_ids": ObjectId(event_id)}},
    )
