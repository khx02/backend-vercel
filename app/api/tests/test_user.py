from fastapi import HTTPException
import pytest
from unittest.mock import AsyncMock, patch

from app.api.user import change_password, create_user
from app.schemas.user import UserCreateReq, ChangePasswordReq
from app.schemas.token import TokenPair
from app.schemas.user import UserModel


@pytest.mark.asyncio
@patch("app.api.user.create_token_pair")
@patch("app.api.user.create_user_service")
async def test_create_user_success(mock_create_user_service, mock_create_token_pair):

    user_create = UserCreateReq(email="addi@addi.com", password="alex's")

    mock_db = AsyncMock()
    mock_user_data = UserModel(
        id="1", email="addi@addi.com", hashed_password="hashed-alex's"
    )

    mock_create_token_pair.return_value = TokenPair(
        access_token="new-access-token",
        refresh_token="new-refresh-token",
        access_expires_at=3600,
        refresh_expires_at=7200,
        token_type="bearer",
    )

    mock_create_user_service.return_value = mock_user_data

    result = await create_user(user_create, mock_db)

    assert isinstance(result.token, TokenPair)
    assert result.user.email == "addi@addi.com"
    assert result.access_token == "new-access-token"


@pytest.mark.asyncio
@patch("app.api.user.create_user_service")
async def test_create_user_failure(mock_create_user_service):

    user_create = UserCreateReq(email="not-addi@not-addi.com", password="not-alex's")

    mock_db = AsyncMock()
    mock_create_user_service.side_effect = HTTPException(
        status_code=400,
        detail="User already exists",
        headers={"WWW-Authenticate": "Bearer"},
    )

    with pytest.raises(HTTPException) as exc_info:
        await create_user(user_create, mock_db)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "User already exists"
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}


@pytest.mark.asyncio
@patch("app.api.user.change_password_service")
async def test_change_password_success(mock_change_password_service):

    user_id = "1"
    email = "addi@addi.com"
    old_password = "old-password"
    new_password = "new-password"
    change_password_req = ChangePasswordReq(
        old_password=old_password, new_password=new_password
    )

    mock_db = AsyncMock()
    mock_change_password_service.return_value = UserModel(
        id=user_id, email=email, hashed_password="hashed-new-alex's"
    )

    result = await change_password(change_password_req, mock_db)

    assert result.id == user_id
    assert result.email == email
    assert result.hashed_password == "hashed-new-alex's"


@pytest.mark.asyncio
@patch("app.api.user.change_password_service")
async def test_change_password_failure(mock_change_password_service):
    change_password_req = ChangePasswordReq(
        old_password="old-password", new_password="new-password"
    )

    mock_db = AsyncMock()
    mock_change_password_service.side_effect = ValueError("Invalid password")

    with pytest.raises(HTTPException) as exc_info:
        await change_password(change_password_req, mock_db)

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Invalid password"
