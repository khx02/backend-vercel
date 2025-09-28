from unittest.mock import AsyncMock, patch

import pytest

from app.api.user import (
    change_password,
    create_user,
    get_current_user,
    get_current_user_teams,
    get_user_by_id,
    verify_code,
)
from app.schemas.team import TeamModel
from app.schemas.user import (
    ChangePasswordRequest,
    ChangePasswordResponse,
    CreateUserRequest,
    CreateUserResponse,
    GetCurrentUserResponse,
    GetCurrentUserTeamsResponse,
    GetUserByIdResponse,
    UserModel,
    VerifyCodeRequest,
    VerifyCodeResponse,
)

from app.test_shared.constants import *


@pytest.mark.asyncio
@patch("app.api.user.create_user_service")
async def test_create_user_success(mock_create_user_service):
    mock_db = AsyncMock()
    create_user_request = CreateUserRequest(
        email=MOCK_USER_EMAIL,
        password=MOCK_USER_PASSWORD,
        first_name=MOCK_USER_FIRST_NAME,
        last_name=MOCK_USER_LAST_NAME,
    )
    mock_create_user_response = CreateUserResponse()
    mock_create_user_service.return_value = mock_create_user_response

    result = await create_user(create_user_request, mock_db)

    assert isinstance(result, CreateUserResponse)


@pytest.mark.asyncio
@patch("app.api.user.verify_code_service")
async def test_verify_code_success(mock_verify_code_service):
    mock_db = AsyncMock()
    verify_code_request = VerifyCodeRequest(
        email=MOCK_USER_EMAIL, verification_code=MOCK_VERIFICATION_CODE
    )
    mock_verify_code_response = VerifyCodeResponse(
        user=UserModel(
            id=MOCK_USER_ID,
            email=MOCK_USER_EMAIL,
        )
    )
    mock_verify_code_service.return_value = mock_verify_code_response

    result = await verify_code(verify_code_request, mock_db)

    assert isinstance(result, VerifyCodeResponse)


@pytest.mark.asyncio
async def test_get_current_user_info_success():
    mock_current_user = UserModel(
        id=MOCK_USER_ID,
        email=MOCK_USER_EMAIL,
        first_name=MOCK_USER_FIRST_NAME,
        last_name=MOCK_USER_LAST_NAME,
    )

    result = await get_current_user(mock_current_user)

    assert isinstance(result, GetCurrentUserResponse)
    assert result.user.id == MOCK_USER_ID
    assert result.user.email == MOCK_USER_EMAIL
    assert result.user.first_name == MOCK_USER_FIRST_NAME
    assert result.user.last_name == MOCK_USER_LAST_NAME


@pytest.mark.asyncio
@patch("app.api.user.get_user_by_id_service")
async def test_get_user_by_id_success(mock_get_user_by_id_service):
    mock_db = AsyncMock()
    mock_get_user_by_id_service.return_value = UserModel(
        id=MOCK_USER_ID,
        email=MOCK_USER_EMAIL,
        first_name=MOCK_USER_FIRST_NAME,
        last_name=MOCK_USER_LAST_NAME,
    )

    result = await get_user_by_id(MOCK_USER_ID, mock_db)

    assert isinstance(result, GetUserByIdResponse)
    assert result.user.id == MOCK_USER_ID
    assert result.user.email == MOCK_USER_EMAIL


@pytest.mark.asyncio
@patch("app.api.user.get_current_user_teams_service")
async def test_get_current_user_teams_success(mock_get_current_user_teams_service):
    mock_db = AsyncMock()
    mock_current_user = UserModel(
        id=MOCK_USER_ID,
        email=MOCK_USER_EMAIL,
    )
    mock_get_current_user_teams_service.return_value = GetCurrentUserTeamsResponse(
        teams=[
            TeamModel(
                id=MOCK_TEAM_ID,
                short_id=MOCK_TEAM_SHORT_ID,
                name=MOCK_TEAM_NAME,
                member_ids=[MOCK_USER_ID],
                exec_member_ids=[MOCK_USER_ID],
                project_ids=[],
                event_ids=[],
            )
        ]
    )

    result = await get_current_user_teams(mock_current_user, mock_db)

    assert isinstance(result, GetCurrentUserTeamsResponse)
    assert len(result.teams) == 1
    assert result.teams[0].id == MOCK_TEAM_ID
    assert result.teams[0].name == MOCK_TEAM_NAME
    assert result.teams[0].member_ids == [MOCK_USER_ID]
    assert result.teams[0].exec_member_ids == [MOCK_USER_ID]
    assert result.teams[0].project_ids == []


@pytest.mark.asyncio
@patch("app.api.user.change_password_service")
async def test_change_password_success(mock_change_password_service):
    mock_db = AsyncMock()
    mock_current_user = UserModel(
        id=MOCK_USER_ID,
        email=MOCK_USER_EMAIL,
    )
    mock_change_password_request = ChangePasswordRequest(
        old_password=MOCK_USER_PASSWORD, new_password=MOCK_USER_NEW_PASSWORD
    )
    mock_change_password_service.return_value = ChangePasswordResponse()

    result = await change_password(
        mock_change_password_request, mock_current_user, mock_db
    )

    assert isinstance(result, ChangePasswordResponse)
