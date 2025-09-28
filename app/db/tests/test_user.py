from datetime import datetime
from unittest.mock import AsyncMock

from bson import ObjectId
import pytest

from app.core.constants import TEAMS_COLLECTION
from app.db.user import (
    db_create_pending_verification,
    db_create_user,
    db_delete_pending_verification,
    db_get_pending_verification,
    db_get_user_by_email,
    db_get_user_by_id,
    db_get_user_teams_by_id,
    db_update_password,
)
from app.test_shared.constants import *


@pytest.mark.asyncio
async def test_db_create_user_success():
    mock_db = AsyncMock()
    mock_users_collection = AsyncMock()
    mock_users_collection.insert_one.return_value = AsyncMock(
        inserted_id=ObjectId(MOCK_INSERTED_ID)
    )
    mock_db.__getitem__.return_value = mock_users_collection

    result = await db_create_user(
        MOCK_USER_EMAIL,
        MOCK_USER_PASSWORD_HASHED,
        MOCK_USER_FIRST_NAME,
        MOCK_USER_LAST_NAME,
        mock_db,
    )

    assert isinstance(result, dict)
    assert result["_id"] == MOCK_INSERTED_ID
    assert result["email"] == MOCK_USER_EMAIL
    assert result["hashed_password"] == MOCK_USER_PASSWORD_HASHED
    assert result["first_name"] == MOCK_USER_FIRST_NAME
    assert result["last_name"] == MOCK_USER_LAST_NAME


@pytest.mark.asyncio
async def test_get_current_user_teams_service_success():
    mock_db = AsyncMock()
    mock_db[TEAMS_COLLECTION].find.return_value.to_list = AsyncMock(
        return_value=[
            {
                "_id": ObjectId(MOCK_TEAM_ID),
                "short_id": MOCK_TEAM_SHORT_ID,
                "name": MOCK_TEAM_NAME,
                "member_ids": [ObjectId(MOCK_USER_ID)],
                "exec_member_ids": [ObjectId(MOCK_USER_ID)],
                "project_ids": [ObjectId(MOCK_PROJECT_ID)],
            },
            {
                "_id": ObjectId(MOCK_TEAM_2_ID),
                "short_id": MOCK_TEAM_2_SHORT_ID,
                "name": MOCK_TEAM_2_NAME,
                "member_ids": [ObjectId(MOCK_USER_2_ID)],
                "exec_member_ids": [ObjectId(MOCK_USER_2_ID)],
                "project_ids": [ObjectId(MOCK_PROJECT_2_ID)],
            },
        ]
    )

    result = await db_get_user_teams_by_id(MOCK_USER_ID, mock_db)

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["_id"] == MOCK_TEAM_ID
    assert result[1]["_id"] == MOCK_TEAM_2_ID


@pytest.mark.asyncio
async def test_db_get_user_by_id_success():
    mock_db = AsyncMock()
    mock_users_collection = AsyncMock()
    mock_users_collection.find_one.return_value = {
        "_id": ObjectId(MOCK_USER_ID),
        "email": MOCK_USER_EMAIL,
        "hashed_password": MOCK_USER_PASSWORD_HASHED,
    }
    mock_db.__getitem__.return_value = mock_users_collection

    result = await db_get_user_by_id(MOCK_USER_ID, mock_db)

    assert isinstance(result, dict)
    assert result["_id"] == MOCK_USER_ID
    assert result["email"] == MOCK_USER_EMAIL
    assert result["hashed_password"] == MOCK_USER_PASSWORD_HASHED


@pytest.mark.asyncio
async def test_db_get_user_by_email_success():
    mock_db = AsyncMock()
    mock_users_collection = AsyncMock()
    mock_users_collection.find_one.return_value = {
        "_id": ObjectId(MOCK_USER_ID),
        "email": MOCK_USER_EMAIL,
        "hashed_password": MOCK_USER_PASSWORD_HASHED,
    }
    mock_db.__getitem__.return_value = mock_users_collection

    result = await db_get_user_by_email(MOCK_USER_EMAIL, mock_db)

    assert isinstance(result, dict)
    assert result["_id"] == MOCK_USER_ID
    assert result["email"] == MOCK_USER_EMAIL
    assert result["hashed_password"] == MOCK_USER_PASSWORD_HASHED


@pytest.mark.asyncio
async def test_db_create_pending_verification_success():
    mock_db = AsyncMock()
    mock_pending_verification_collection = AsyncMock()
    mock_db.__getitem__.return_value = mock_pending_verification_collection

    result = await db_create_pending_verification(
        MOCK_USER_EMAIL,
        MOCK_VERIFICATION_CODE,
        MOCK_USER_PASSWORD_HASHED,
        MOCK_USER_FIRST_NAME,
        MOCK_USER_LAST_NAME,
        mock_db,
    )

    assert result is None


@pytest.mark.asyncio
async def test_db_get_pending_verification_success():
    mock_db = AsyncMock()
    mock_current_time = datetime.now()
    mock_pending_verification_collection = AsyncMock()
    mock_pending_verification_collection.find_one.return_value = {
        "email": MOCK_USER_EMAIL,
        "verification_code": MOCK_VERIFICATION_CODE,
        "hashed_password": MOCK_USER_PASSWORD_HASHED,
        "created_at": mock_current_time,
    }
    mock_db.__getitem__.return_value = mock_pending_verification_collection

    result = await db_get_pending_verification(MOCK_USER_EMAIL, mock_db)

    assert isinstance(result, dict)
    assert result["email"] == MOCK_USER_EMAIL
    assert result["verification_code"] == MOCK_VERIFICATION_CODE
    assert result["hashed_password"] == MOCK_USER_PASSWORD_HASHED
    assert result["created_at"] == mock_current_time


@pytest.mark.asyncio
async def test_db_delete_pending_verification_success():
    mock_db = AsyncMock()
    mock_pending_verification_collection = AsyncMock()
    mock_db.__getitem__.return_value = mock_pending_verification_collection

    result = await db_delete_pending_verification(MOCK_USER_EMAIL, mock_db)

    assert result is None


@pytest.mark.asyncio
async def test_db_get_user_or_none_by_email_success_user_case():
    mock_db = AsyncMock()
    mock_users_collection = AsyncMock()
    mock_users_collection.find_one.return_value = {
        "_id": ObjectId(MOCK_USER_ID),
        "email": MOCK_USER_EMAIL,
        "hashed_password": MOCK_USER_PASSWORD_HASHED,
    }
    mock_db.__getitem__.return_value = mock_users_collection

    result = await db_get_user_by_email(MOCK_USER_EMAIL, mock_db)

    assert isinstance(result, dict)
    assert result["_id"] == MOCK_USER_ID
    assert result["email"] == MOCK_USER_EMAIL
    assert result["hashed_password"] == MOCK_USER_PASSWORD_HASHED


@pytest.mark.asyncio
async def test_db_get_user_or_none_by_email_failure_none_case():
    mock_db = AsyncMock()
    mock_users_collection = AsyncMock()
    mock_users_collection.find_one.return_value = None
    mock_db.__getitem__.return_value = mock_users_collection

    result = await db_get_user_by_email(MOCK_USER_EMAIL, mock_db)

    assert result is None


@pytest.mark.asyncio
async def test_db_update_password_success():
    mock_db = AsyncMock()
    mock_users_collection = AsyncMock()
    mock_users_collection.update_one.return_value = AsyncMock()
    mock_db.__getitem__.return_value = mock_users_collection

    result = await db_update_password(
        MOCK_USER_ID, MOCK_USER_NEW_PASSWORD_HASHED, mock_db
    )

    assert result is None
