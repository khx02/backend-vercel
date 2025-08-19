from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from app.api.user import change_password, create_user
from app.schemas.token import TokenPair
from app.schemas.user import ChangePasswordReq, UserCreateReq, UserModel


@pytest.mark.asyncio
@patch("app.api.user.create_user_service")
async def test_create_user_success(mock_create_user_service):

    user_create = UserCreateReq(email="addi@addi.com", password="alex's")

    mock_db = AsyncMock()
    mock_user_data = UserModel(
        id="1", email="addi@addi.com", hashed_password="hashed-alex's"
    )

    mock_create_user_service.return_value = mock_user_data

    result = await create_user(user_create, mock_db)

    assert isinstance(result, UserModel)
    assert result.id == "1"
    assert result.email == "addi@addi.com"
    assert result.hashed_password == "hashed-alex's"


@pytest.mark.asyncio
@patch("app.api.user.create_user_service")
async def test_create_user_failure(mock_create_user_service):

    user_create = UserCreateReq(email="not-addi@not-addi.com", password="not-alex's")

    mock_db = AsyncMock()
    mock_create_user_service.side_effect = ValueError("User already exists")

    with pytest.raises(HTTPException) as exc_info:
        await create_user(user_create, mock_db)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "User already exists"


@pytest.mark.asyncio
@patch("app.api.user.change_password_service")
async def test_change_password_success(mock_change_password_service):

    user_id = "1"
    email = "addi@addi.com"
    mock_current_user = UserModel(
        id=user_id, email=email, hashed_password="hashed-old-alex's"
    )

    old_password = "old-alex's"
    new_password = "new-alex's"
    change_password_req = ChangePasswordReq(
        old_password=old_password, new_password=new_password
    )

    mock_db = AsyncMock()
    mock_change_password_service.return_value = UserModel(
        id=user_id, email=email, hashed_password="hashed-new-alex's"
    )

    result = await change_password(change_password_req, mock_current_user, mock_db)

    assert isinstance(result, UserModel)
    assert result.id == user_id
    assert result.email == email
    assert result.hashed_password == "hashed-new-alex's"


@pytest.mark.asyncio
@patch("app.api.user.change_password_service")
async def test_change_password_failure(mock_change_password_service):
    user_id = "1"
    email = "addi@addi.com"
    mock_current_user = UserModel(
        id=user_id, email=email, hashed_password="hashed-old-alex's"
    )

    change_password_req = ChangePasswordReq(
        old_password="old-alex's", new_password="new-alex's"
    )

    mock_db = AsyncMock()
    mock_change_password_service.side_effect = ValueError("Invalid password")

    with pytest.raises(HTTPException) as exc_info:
        await change_password(change_password_req, mock_current_user, mock_db)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid password"


@pytest.mark.asyncio
@patch("app.api.user.change_password_service")
async def test_change_password_server_error(mock_change_password_service):
    """Test change password with unexpected server error."""
    user_id = "1"
    email = "addi@addi.com"
    mock_current_user = UserModel(
        id=user_id, email=email, hashed_password="hashed-old-alex's"
    )

    change_password_req = ChangePasswordReq(
        old_password="old-alex's", new_password="new-alex's"
    )

    mock_db = AsyncMock()
    # Simulate unexpected exception (not ValueError)
    mock_change_password_service.side_effect = RuntimeError("Database error")

    with pytest.raises(HTTPException) as exc_info:
        await change_password(change_password_req, mock_current_user, mock_db)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Failed to change password"
