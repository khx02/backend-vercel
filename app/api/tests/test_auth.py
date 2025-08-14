import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.security import OAuth2PasswordRequestForm

from app.api.auth import (
    login_for_token_access,
    get_current_user,
    authenticate_user,
    validate_token,
    refresh_token,
)
from app.schemas.token import TokenPair
from app.schemas.user import UserModel


@pytest.mark.asyncio
@patch("app.api.auth.get_user_service")
@patch("app.api.auth.jwt.decode")
async def test_get_current_user(mock_decode, mock_get_user_service):
    mock_db = AsyncMock()

    mock_token = "fake-jwt-token"
    mock_decode.return_value = {"sub": "addi@addi.com"}

    mock_user = UserModel(
        id="1", email="addi@addi.com", hashed_password="hashed-meow's"
    )
    mock_get_user_service.return_value = mock_user

    result = await get_current_user(mock_db, mock_token)

    assert result.id == "1"
    assert result.email == "addi@addi.com"
    assert result.hashed_password == "hashed-meow's"


@pytest.mark.asyncio
@patch("app.api.auth.get_user_service")
@patch("app.api.auth.verify_password")
async def test_authenticate_user(mock_verify_password, mock_get_user_service):
    mock_db = AsyncMock()
    mock_email = "addi@addi.com"
    mock_password = "meow's"

    mock_user = UserModel(id="1", email=mock_email, hashed_password="hashed-meow's")
    mock_get_user_service.return_value = mock_user
    mock_verify_password.return_value = True

    result = await authenticate_user(mock_db, mock_email, mock_password)
    assert result.id == "1"
    assert result.email == mock_email
    assert result.hashed_password == "hashed-meow's"


@pytest.mark.asyncio
@patch("app.api.auth.authenticate_user")
async def test_login_for_token_access(mock_authenticate_user):
    form_data = MagicMock(spec=OAuth2PasswordRequestForm)
    form_data.username = "addi@addi.com"
    form_data.password = "meow's"

    mock_db = AsyncMock()

    mock_user = UserModel(
        id="1", email="addi@addi.com", hashed_password="hashed-meow's"
    )

    mock_authenticate_user.return_value = mock_user

    result = await login_for_token_access(form_data, mock_db)

    assert result.user.email == "addi@addi.com"
    assert result.access_token is not None


@pytest.mark.asyncio
async def test_validate_token():
    mock_user = UserModel(
        id="1", email="addi@addi.com", hashed_password="hashed-meow's"
    )

    result = await validate_token(mock_user)

    assert result.is_valid is True


@pytest.mark.asyncio
@patch("app.api.auth.create_token_pair")
@patch("app.api.auth.get_user_service")
@patch("app.api.auth.jwt.decode")
async def test_refresh_token(
    mock_decode, mock_get_user_service, mock_create_token_pair
):
    mock_db = AsyncMock()
    mock_email = "addi@addi.com"

    mock_decode.return_value = {"sub": mock_email}
    mock_user = UserModel(id="1", email=mock_email, hashed_password="hashed-meow's")
    mock_get_user_service.return_value = mock_user

    mock_create_token_pair.return_value = TokenPair(
        access_token="new-access-token",
        refresh_token="new-refresh-token",
        access_expires_at=3600,
        refresh_expires_at=7200,
        token_type="bearer",
    )

    result = await refresh_token(mock_db)

    assert isinstance(result.token, TokenPair)
    assert result.user.email == mock_email
    assert result.access_token is not None
