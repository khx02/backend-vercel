import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm

from app.api.auth import (
    login_for_token_access,
    get_current_user,
    authenticate_user,
    refresh_token,
)
from app.schemas.token import TokenPair, RefreshTokenReq
from app.schemas.user import UserModel


@pytest.mark.asyncio
@patch("app.api.auth.get_user_service")
@patch("app.api.auth.jwt.decode")
async def test_get_current_user_success(mock_decode, mock_get_user_service):
    mock_db = AsyncMock()

    mock_token = "fake-jwt-token"
    mock_decode.return_value = {"sub": "addi@addi.com"}

    mock_user = UserModel(
        id="1", email="addi@addi.com", hashed_password="hashed-alex's"
    )
    mock_get_user_service.return_value = mock_user

    result = await get_current_user(mock_token, mock_db)

    assert result.id == "1"
    assert result.email == "addi@addi.com"
    assert result.hashed_password == "hashed-alex's"


@pytest.mark.asyncio
@patch("app.api.auth.jwt.decode")
async def test_get_current_user_failure(mock_decode):
    mock_db = AsyncMock()

    mock_token = "fake-jwt-token"
    mock_decode.return_value = {}

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(mock_token, mock_db)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}


@pytest.mark.asyncio
@patch("app.api.auth.get_user_service")
@patch("app.api.auth.verify_password")
async def test_authenticate_user_success(mock_verify_password, mock_get_user_service):
    mock_db = AsyncMock()
    mock_email = "addi@addi.com"
    mock_password = "alex's"

    mock_user = UserModel(id="1", email=mock_email, hashed_password="hashed-alex's")
    mock_get_user_service.return_value = mock_user
    mock_verify_password.return_value = True

    result = await authenticate_user(mock_db, mock_email, mock_password)
    assert result.id == "1"
    assert result.email == mock_email
    assert result.hashed_password == "hashed-alex's"


@pytest.mark.asyncio
@patch("app.api.auth.get_user_service")
async def test_authenticate_user_failure(mock_get_user_service):
    mock_db = AsyncMock()
    mock_email = "not-addi@not-addi.com"
    mock_password = "not-alex's"

    mock_get_user_service.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await authenticate_user(mock_db, mock_email, mock_password)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Incorrect username or password"


@pytest.mark.asyncio
@patch("app.api.auth.authenticate_user")
@patch("app.api.auth.create_token_pair")
async def test_login_for_token_access(mock_create_token_pair, mock_authenticate_user):
    # Mock the Response object
    mock_response = MagicMock(spec=Response)
    
    form_data = MagicMock(spec=OAuth2PasswordRequestForm)
    form_data.username = "addi@addi.com"
    form_data.password = "alex's"

    mock_db = AsyncMock()

    mock_user = UserModel(
        id="1", email="addi@addi.com", hashed_password="hashed-alex's"
    )

    mock_authenticate_user.return_value = mock_user
    
    # Mock the token pair creation
    mock_token_pair = TokenPair(
        access_token="test-access-token",
        refresh_token="test-refresh-token",
        access_expires_at=3600,
        refresh_expires_at=7200,
        token_type="bearer"
    )
    mock_create_token_pair.return_value = mock_token_pair

    result = await login_for_token_access(mock_response, form_data, mock_db)

    assert result.user.email == "addi@addi.com"
    assert result.access_token == "test-access-token"
    # Verify that set_cookie was called on the response
    assert mock_response.set_cookie.call_count == 2


@pytest.mark.asyncio
@patch("app.api.auth.authenticate_user")
async def test_login_for_token_access_failure(mock_authenticate_user):
    # Mock the Response object
    mock_response = MagicMock(spec=Response)
    
    form_data = MagicMock(spec=OAuth2PasswordRequestForm)
    form_data.username = "not-addi@not-addi.com"
    form_data.password = "not-alex's"

    mock_db = AsyncMock()

    mock_authenticate_user.side_effect = HTTPException(
        status_code=401,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    with pytest.raises(HTTPException) as exc_info:
        await login_for_token_access(mock_response, form_data, mock_db)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Incorrect username or password"
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}


@pytest.mark.asyncio
@patch("app.api.auth.create_token_pair")
@patch("app.api.auth.get_user_service")
@patch("app.api.auth.jwt.decode")
async def test_refresh_token_success(
    mock_decode, mock_get_user_service, mock_create_token_pair
):
    # Mock the Response object
    mock_response = MagicMock(spec=Response)
    
    mock_db = AsyncMock()
    mock_email = "addi@addi.com"

    mock_decode.return_value = {"sub": mock_email}
    mock_user = UserModel(id="1", email=mock_email, hashed_password="hashed-alex's")
    mock_get_user_service.return_value = mock_user

    mock_create_token_pair.return_value = TokenPair(
        access_token="new-access-token",
        refresh_token="new-refresh-token",
        access_expires_at=3600,
        refresh_expires_at=7200,
        token_type="bearer",
    )

    # Use refresh_token_cookie parameter instead of RefreshTokenReq
    result = await refresh_token(mock_response, "old-refresh-token", mock_db)

    assert result.user.email == mock_email
    assert result.access_token == "new-access-token"
    # Verify that set_cookie was called on the response to rotate tokens
    assert mock_response.set_cookie.call_count == 2


@pytest.mark.asyncio
@patch("app.api.auth.jwt.decode")
async def test_refresh_token_failure(mock_decode):
    # Mock the Response object
    mock_response = MagicMock(spec=Response)
    
    mock_db = AsyncMock()

    # Use None to simulate missing refresh token cookie
    mock_decode.return_value = {}

    with pytest.raises(HTTPException) as exc_info:
        await refresh_token(mock_response, "invalid-refresh-token", mock_db)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid refresh token"


@pytest.mark.asyncio
async def test_refresh_token_missing_token():
    # Mock the Response object
    mock_response = MagicMock(spec=Response)
    
    mock_db = AsyncMock()

    with pytest.raises(HTTPException) as exc_info:
        await refresh_token(mock_response, None, mock_db)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "No refresh token"
