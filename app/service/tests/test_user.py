from math import e
from unittest.mock import AsyncMock, patch

from fastapi import HTTPException
import pytest

from app.schemas.user import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    CreateUserRequest,
    CreateUserResponse,
    GetCurrentUserTeamsResponse,
)
from app.service.user import (
    change_password_service,
    create_user_service,
    get_current_user_teams_service,
)

from app.test_shared.constants import *


@pytest.mark.asyncio
@patch("app.service.user.db_create_user")
@patch("app.service.user.hash_password")
@patch("app.service.user.db_get_user_by_email")
async def test_create_user_service_success(
    mock_db_get_user_by_email, mock_hash_password, mock_db_create_user
):
    mock_db = AsyncMock()
    mock_db_get_user_by_email.return_value = None
    mock_hash_password.return_value = MOCK_USER_PASSWORD_HASHED
    mock_db_create_user.return_value = {
        "_id": MOCK_USER_ID,
        "email": MOCK_USER_EMAIL,
        "hashed_password": MOCK_USER_PASSWORD_HASHED,
    }
    mock_create_user_request = CreateUserRequest(
        email=MOCK_USER_EMAIL, password=MOCK_USER_PASSWORD
    )

    result = await create_user_service(mock_create_user_request, mock_db)

    assert isinstance(result, CreateUserResponse)
    assert result.user.id == MOCK_USER_ID
    assert result.user.email == MOCK_USER_EMAIL


@pytest.mark.asyncio
@patch("app.service.user.db_get_user_by_email")
async def test_create_user_service_failure(mock_db_get_user_by_email):
    mock_db = AsyncMock()
    mock_db_get_user_by_email.return_value = {
        "_id": MOCK_USER_ID,
        "email": MOCK_USER_EMAIL,
        "hashed_password": MOCK_USER_PASSWORD_HASHED,
    }
    mock_create_user_request = CreateUserRequest(
        email=MOCK_USER_EMAIL, password=MOCK_USER_PASSWORD
    )

    with pytest.raises(HTTPException) as exc_info:
        await create_user_service(mock_create_user_request, mock_db)

    assert exc_info.value.status_code == 400
    assert (
        exc_info.value.detail
        == f"A user has already been created using this email address: email={MOCK_USER_EMAIL}"
    )


@pytest.mark.asyncio
@patch("app.service.user.db_get_user_teams_by_id")
@patch("app.service.user.db_get_user_by_id")
async def test_get_current_user_teams_service_success(
    mock_db_get_user_by_id, mock_db_get_user_teams_by_id
):
    mock_db = AsyncMock()
    mock_db_get_user_by_id.return_value = {
        "_id": MOCK_USER_ID,
        "email": MOCK_USER_EMAIL,
        "hashed_password": MOCK_USER_PASSWORD_HASHED,
    }
    mock_db_get_user_teams_by_id.return_value = [
        {
            "_id": MOCK_TEAM_ID,
            "name": MOCK_TEAM_NAME,
            "member_ids": [MOCK_USER_ID],
            "exec_member_ids": [MOCK_USER_ID],
            "project_ids": [MOCK_PROJECT_ID],
        }
    ]

    result = await get_current_user_teams_service(MOCK_USER_ID, mock_db)

    assert isinstance(result, GetCurrentUserTeamsResponse)
    assert isinstance(result.teams, list)
    assert len(result.teams) == 1
    assert result.teams[0].id == MOCK_TEAM_ID
    assert result.teams[0].name == MOCK_TEAM_NAME
    assert result.teams[0].member_ids == [MOCK_USER_ID]
    assert result.teams[0].exec_member_ids == [MOCK_USER_ID]
    assert result.teams[0].project_ids == [MOCK_PROJECT_ID]


@pytest.mark.asyncio
@patch("app.service.user.db_update_password")
@patch("app.service.user.hash_password")
@patch("app.service.user.verify_password")
@patch("app.service.user.db_get_user_by_id")
async def test_change_password_service(
    mock_db_get_user_by_id,
    mock_verify_password,
    mock_hash_password,
    mock_db_update_password,
):
    mock_db = AsyncMock()
    mock_db_get_user_by_id.return_value = {
        "_id": MOCK_USER_ID,
        "email": MOCK_USER_EMAIL,
        "hashed_password": MOCK_USER_PASSWORD_HASHED,
    }
    mock_verify_password.return_value = True
    mock_hash_password.return_value = MOCK_USER_NEW_PASSWORD_HASHED
    mock_db_update_password.return_value = None
    mock_change_password_request = ChangePasswordRequest(
        old_password=MOCK_USER_PASSWORD, new_password=MOCK_USER_NEW_PASSWORD
    )

    result = await change_password_service(
        MOCK_USER_ID, mock_change_password_request, mock_db
    )

    assert isinstance(result, ChangePasswordResponse)
