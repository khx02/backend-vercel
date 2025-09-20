from unittest.mock import AsyncMock, MagicMock, patch

import jwt
import pytest
from fastapi import HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.auth import (
    authenticate_user,
    clear_auth_cookies,
    get_current_user_info,
    get_current_user_info_from_cookie,
    get_current_user_info_from_token,
    login_for_token_access,
    refresh_token,
    set_auth_cookies,
)
from app.schemas.token import TokenPair
from app.schemas.user import UserModel


@pytest.mark.asyncio
@patch("app.api.auth.get_user_service")
@patch("app.api.auth.get_hashed_password_service")
@patch("app.api.auth.verify_password")
async def test_authenticate_user_success(
    mock_verify_password, mock_get_hashed_password_service, mock_get_user_service
):
    mock_db = AsyncMock()
    mock_email = "addi@addi.com"
    mock_password = "alex's"

    mock_user = UserModel(id="1", email=mock_email)
    mock_get_user_service.return_value = mock_user
    mock_verify_password.return_value = True
    mock_get_hashed_password_service.return_value = "hashed_password"

    result = await authenticate_user(mock_db, mock_email, mock_password)
    assert result.id == "1"
    assert result.email == mock_email


@pytest.mark.asyncio
@patch("app.api.auth.get_hashed_password_service")
@patch("app.api.auth.get_user_service")
async def test_authenticate_user_failure(
    mock_get_hashed_password_service, mock_get_user_service
):
    mock_db = AsyncMock()
    mock_email = "not-addi@not-addi.com"
    mock_password = "not-alex's"

    mock_get_user_service.return_value = None
    mock_get_hashed_password_service.return_value = "hashed_password"

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

    mock_user = UserModel(id="1", email="addi@addi.com")

    mock_authenticate_user.return_value = mock_user

    # Mock the token pair creation
    mock_token_pair = TokenPair(
        access_token="test-access-token",
        refresh_token="test-refresh-token",
        access_expires_at=3600,
        refresh_expires_at=7200,
        token_type="bearer",
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
    mock_user = UserModel(id="1", email=mock_email)
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


def test_set_auth_cookies():
    """Test setting authentication cookies."""
    mock_response = MagicMock(spec=Response)
    access_token = "test-access-token"
    refresh_token = "test-refresh-token"

    set_auth_cookies(mock_response, access_token, refresh_token)

    # Verify set_cookie was called twice (access and refresh)
    assert mock_response.set_cookie.call_count == 2

    # Check the first call (access token)
    first_call = mock_response.set_cookie.call_args_list[0]
    assert first_call[1]["key"] == "access_token"
    assert first_call[1]["value"] == access_token
    assert first_call[1]["httponly"] is True
    assert first_call[1]["max_age"] == 60 * 15  # 15 minutes

    # Check the second call (refresh token)
    second_call = mock_response.set_cookie.call_args_list[1]
    assert second_call[1]["key"] == "refresh_token"
    assert second_call[1]["value"] == refresh_token
    assert second_call[1]["httponly"] is True
    assert second_call[1]["max_age"] == 60 * 60 * 24 * 14  # 14 days


def test_clear_auth_cookies():
    """Test clearing authentication cookies."""
    mock_response = MagicMock(spec=Response)

    clear_auth_cookies(mock_response)

    # Verify delete_cookie was called twice
    assert mock_response.delete_cookie.call_count == 2

    # Check the calls
    calls = mock_response.delete_cookie.call_args_list
    cookie_names = [call[0][0] for call in calls]  # First positional argument
    assert "access_token" in cookie_names
    assert "refresh_token" in cookie_names


@pytest.mark.asyncio
@patch("app.api.auth.get_current_user_from_cookie")
async def test_get_current_user_cookie_available_success(
    mock_get_current_user_from_cookie,
):
    mock_user = UserModel(id="1", email="addi@addi.com")
    mock_get_current_user_from_cookie.return_value = mock_user

    result = await get_current_user_info()

    assert result.id == "1"
    assert result.email == "addi@addi.com"


@pytest.mark.asyncio
@patch("app.api.auth.get_current_user_from_token")
@patch("app.api.auth.get_current_user_from_cookie")
async def test_get_current_user_token_available_success(
    mock_get_current_user_from_cookie, mock_get_current_user_from_token
):
    mock_user = UserModel(id="1", email="addi@addi.com")
    mock_get_current_user_from_cookie.side_effect = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
    )
    mock_get_current_user_from_token.return_value = mock_user

    result = await get_current_user_info()

    assert result.id == "1"
    assert result.email == "addi@addi.com"


@pytest.mark.asyncio
@patch("app.api.auth.get_current_user_from_token")
@patch("app.api.auth.get_current_user_from_cookie")
async def test_get_current_user_cookie_token_not_available_failure(
    mock_get_current_user_from_cookie, mock_get_current_user_from_token
):
    mock_get_current_user_from_cookie.side_effect = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
    )
    mock_get_current_user_from_token.side_effect = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user_info()

    assert exc_info.value.status_code == 401
    assert (
        exc_info.value.detail
        == "Cookie: 401: Not authenticated, Token: 401: Not authenticated"
    )


@pytest.mark.asyncio
@patch("app.api.auth.get_user_service")
@patch("app.api.auth.jwt.decode")
async def test_get_current_user_from_cookie_success(mock_decode, mock_get_user_service):
    """Test successful user retrieval from cookie."""
    mock_db = AsyncMock()
    access_token = "valid-access-token"

    mock_decode.return_value = {"sub": "test@example.com"}
    mock_user = UserModel(id="1", email="test@example.com")
    mock_get_user_service.return_value = mock_user

    result = await get_current_user_info_from_cookie(access_token, mock_db)

    assert result.email == "test@example.com"
    assert result.id == "1"


@pytest.mark.asyncio
async def test_get_current_user_from_cookie_no_token():
    """Test user retrieval with no access token."""
    mock_db = AsyncMock()

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user_info_from_cookie(None, mock_db)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Not authenticated"


@pytest.mark.asyncio
@patch("app.api.auth.get_user_service")
@patch("app.api.auth.jwt.decode")
async def test_get_current_user_from_token_success(mock_decode, mock_get_user_service):
    mock_db = AsyncMock()

    mock_token = "fake-jwt-token"
    mock_decode.return_value = {"sub": "addi@addi.com"}

    mock_user = UserModel(id="1", email="addi@addi.com")
    mock_get_user_service.return_value = mock_user

    result = await get_current_user_info_from_token(mock_token, mock_db)

    assert result.id == "1"
    assert result.email == "addi@addi.com"


@pytest.mark.asyncio
@patch("app.api.auth.jwt.decode")
async def test_get_current_user_from_token_failure(mock_decode):
    mock_db = AsyncMock()

    mock_token = "fake-jwt-token"
    mock_decode.return_value = {}

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user_info_from_token(mock_token, mock_db)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"
    assert exc_info.value.headers == {"WWW-Authenticate": "Bearer"}


@pytest.mark.asyncio
@patch("app.api.auth.jwt.decode")
async def test_get_current_user_from_cookie_invalid_token(mock_decode):
    """Test user retrieval with invalid token."""
    mock_db = AsyncMock()
    access_token = "invalid-token"

    mock_decode.side_effect = jwt.InvalidTokenError("Invalid token")

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user_info_from_cookie(access_token, mock_db)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token"


@pytest.mark.asyncio
@patch("app.api.auth.get_user_service")
@patch("app.api.auth.jwt.decode")
async def test_get_current_user_from_cookie_no_email(
    mock_decode, mock_get_user_service
):
    """Test user retrieval when token has no email."""
    mock_db = AsyncMock()
    access_token = "token-without-email"

    mock_decode.return_value = {}  # No 'sub' field

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user_info_from_cookie(access_token, mock_db)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token"


@pytest.mark.asyncio
@patch("app.api.auth.get_user_service")
@patch("app.api.auth.jwt.decode")
async def test_get_current_user_from_cookie_user_not_found(
    mock_decode, mock_get_user_service
):
    """Test user retrieval when user doesn't exist in database."""
    mock_db = AsyncMock()
    access_token = "valid-token"

    mock_decode.return_value = {"sub": "nonexistent@example.com"}
    mock_get_user_service.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user_info_from_cookie(access_token, mock_db)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "User not found"


@pytest.mark.asyncio
@patch("app.api.auth.get_user_service")
async def test_refresh_token_user_not_found(mock_get_user_service):
    """Test refresh token when user is not found."""
    mock_response = MagicMock(spec=Response)
    mock_db = AsyncMock()

    mock_get_user_service.return_value = None

    with patch("app.api.auth.jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "nonexistent@example.com"}

        with pytest.raises(HTTPException) as exc_info:
            await refresh_token(mock_response, "valid-refresh-token", mock_db)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "User not found"
