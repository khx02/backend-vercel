from unittest.mock import AsyncMock
from pymongo.errors import PyMongoError

import pytest
from bson import ObjectId

from app.db.team import *
from app.schemas.project import Project

from app.test_shared.constants import (
    MOCK_USER_ID,
    MOCK_USER_2_ID,
    MOCK_TEAM_NAME,
    MOCK_TEAM_ID,
    MOCK_INSERTED_ID,
    MOCK_PROJECT_NAME,
    MOCK_PROJECT_DESCRIPTION,
)


@pytest.mark.asyncio
async def test_db_create_team_success():
    mock_db = AsyncMock()
    mock_teams_collection = AsyncMock()
    mock_teams_collection.insert_one.return_value = AsyncMock(
        inserted_id=ObjectId(MOCK_INSERTED_ID)
    )
    mock_db.__getitem__.return_value = mock_teams_collection

    result = await db_create_team(MOCK_USER_ID, MOCK_TEAM_NAME, mock_db)

    assert isinstance(result, dict)
    assert result["_id"] == MOCK_INSERTED_ID
    assert result["name"] == MOCK_TEAM_NAME
    assert result["member_ids"] == [MOCK_USER_ID]
    assert result["exec_member_ids"] == [MOCK_USER_ID]
    assert result["project_ids"] == []


@pytest.mark.asyncio
async def test_db_join_team_success():
    mock_db = AsyncMock()
    mock_teams_collection = AsyncMock()
    mock_db.__getitem__.return_value = mock_teams_collection

    result = await db_join_team(MOCK_TEAM_ID, MOCK_USER_ID, mock_db)

    assert result is None


@pytest.mark.asyncio
async def test_db_get_team_by_id_success():
    mock_db = AsyncMock()
    mock_teams_collection = AsyncMock()
    mock_teams_collection.find_one.return_value = {
        "_id": ObjectId(MOCK_TEAM_ID),
        "name": MOCK_TEAM_NAME,
        "member_ids": [MOCK_USER_ID],
        "exec_member_ids": [MOCK_USER_ID],
        "project_ids": [],
    }
    mock_db.__getitem__.return_value = mock_teams_collection

    result = await db_get_team_by_id(MOCK_TEAM_ID, mock_db)

    assert isinstance(result, dict)
    assert result["_id"] == MOCK_TEAM_ID
    assert result["name"] == MOCK_TEAM_NAME
    assert result["member_ids"] == [MOCK_USER_ID]
    assert result["exec_member_ids"] == [MOCK_USER_ID]
    assert result["project_ids"] == []


@pytest.mark.asyncio
async def test_db_promote_team_member_success():
    mock_db = AsyncMock()
    mock_teams_collection = AsyncMock()
    mock_teams_collection.find_one.return_value = {
        "_id": ObjectId(MOCK_TEAM_ID),
        "name": MOCK_TEAM_NAME,
        "member_ids": [MOCK_USER_ID, MOCK_USER_2_ID],
        "exec_member_ids": [MOCK_USER_ID],
        "project_ids": [],
    }
    mock_db.__getitem__.return_value = mock_teams_collection

    result = await db_promote_team_member(MOCK_TEAM_ID, MOCK_USER_2_ID, mock_db)

    assert result is None


@pytest.mark.asyncio
async def test_db_leave_team_success():
    mock_db = AsyncMock()
    mock_teams_collection = AsyncMock()
    mock_teams_collection.find_one.return_value = {
        "_id": ObjectId(MOCK_TEAM_ID),
        "name": MOCK_TEAM_NAME,
        "member_ids": [MOCK_USER_ID, MOCK_USER_2_ID],
        "exec_member_ids": [MOCK_USER_ID],
        "project_ids": [],
    }
    mock_db.__getitem__.return_value = mock_teams_collection

    result = await db_leave_team(MOCK_TEAM_ID, MOCK_USER_ID, mock_db)

    assert result is None


@pytest.mark.asyncio
async def test_db_kick_team_member_success():
    mock_db = AsyncMock()
    mock_teams_collection = AsyncMock()
    mock_teams_collection.find_one.return_value = {
        "_id": ObjectId(MOCK_TEAM_ID),
        "name": MOCK_TEAM_NAME,
        "member_ids": [MOCK_USER_ID, MOCK_USER_2_ID],
        "exec_member_ids": [MOCK_USER_ID],
        "project_ids": [],
    }
    mock_db.__getitem__.return_value = mock_teams_collection

    result = await db_kick_team_member(MOCK_TEAM_ID, MOCK_USER_2_ID, mock_db)

    assert result is None


@pytest.mark.asyncio
async def test_db_create_project_success():
    mock_db = AsyncMock()
    mock_teams_collection = AsyncMock()
    mock_teams_collection.insert_one.return_value = AsyncMock(
        inserted_id=MOCK_INSERTED_ID
    )
    mock_db.__getitem__.return_value = mock_teams_collection
    mock_create_project_request = CreateProjectRequest(
        name=MOCK_PROJECT_NAME, description=MOCK_PROJECT_DESCRIPTION
    )

    result = await db_create_project(MOCK_TEAM_ID, mock_create_project_request, mock_db)

    assert isinstance(result, dict)
    assert result["_id"] == MOCK_INSERTED_ID
    assert result["name"] == MOCK_PROJECT_NAME
    assert result["description"] == MOCK_PROJECT_DESCRIPTION
    assert len(result["todo_statuses"]) == 3
    assert all(
        "id" in status and "name" in status for status in result["todo_statuses"]
    )
