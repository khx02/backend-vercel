from unittest.mock import AsyncMock, patch

import pytest

from app.schemas.user import ChangePasswordReq, UserCreateReq, UserModel
from app.service.user import (
    change_password_service,
    create_user_service,
    get_user_service,
)


@pytest.mark.asyncio
@patch("app.service.user.db_create_user")
@patch("app.service.user.hash_password")
@patch("app.service.user.db_get_user_by_email")
async def test_create_user_service_success(
    mock_db_get_user_by_email, mock_hash_password, mock_db_create_user
):
    user_id = "1"
    user_email = "addi@addi.com"
    user_password = "alex's"
    user_hashed_password = "hashed-alex's"
    user_create_req = UserCreateReq(email=user_email, password=user_password)

    mock_db = AsyncMock()

    mock_db_get_user_by_email.return_value = None
    mock_hash_password.return_value = user_hashed_password
    mock_db_create_user.return_value = {
        "_id": user_id,
        "email": user_email,
        "hashed_password": user_hashed_password,
    }

    result = await create_user_service(mock_db, user_create_req)

    assert result.id == user_id
    assert result.email == user_email
    assert result.hashed_password == user_hashed_password


@pytest.mark.asyncio
@patch("app.service.user.db_get_user_by_email")
async def test_create_user_service_failure(mock_db_get_user_by_email):
    user_id = "1"
    user_email = "addi@addi.com"
    user_password = "alex's"
    user_hashed_password = "hashed-alex's"
    user_create_req = UserCreateReq(email=user_email, password=user_password)

    mock_db = AsyncMock()

    mock_db_get_user_by_email.return_value = {
        "_id": user_id,
        "email": user_email,
        "hashed_password": user_hashed_password,
    }

    with pytest.raises(ValueError) as exc_info:
        await create_user_service(mock_db, user_create_req)

    assert str(exc_info.value) == f"User with email '{user_email}' already exists"


@pytest.mark.asyncio
@patch("app.service.user.db_get_user_by_email")
async def test_get_user_service_success(mock_db_get_user_by_email):
    user_id = "1"
    user_email = "addi@addi.com"
    user_hashed_password = "hashed-alex's"

    mock_db = AsyncMock()
    mock_db_get_user_by_email.return_value = {
        "_id": user_id,
        "email": user_email,
        "hashed_password": user_hashed_password,
    }

    result = await get_user_service(mock_db, user_email)

    assert isinstance(result, UserModel)
    assert result.id == user_id
    assert result.email == user_email
    assert result.hashed_password == user_hashed_password


@pytest.mark.asyncio
@patch("app.service.user.db_get_user_by_email")
async def test_get_user_service_failure(mock_db_get_user_by_email):
    user_email = "addi@addi.com"

    mock_db = AsyncMock()

    mock_db_get_user_by_email.return_value = None

    result = await get_user_service(mock_db, user_email)

    assert result is None


@pytest.mark.asyncio
@patch("app.service.user.db_update_password")
@patch("app.service.user.hash_password")
@patch("app.service.user.verify_password")
@patch("app.service.user.get_user_service")
async def test_change_password_service_success(
    mock_get_user_service,
    mock_verify_password,
    mock_hash_password,
    mock_db_update_password,
):
    user_id = "1"
    user_email = "addi@addi.com"
    old_password = "old-alex's"
    old_password_hashed = "hashed-old-alex's"
    new_password = "new-alex's"

    change_password_req = ChangePasswordReq(
        old_password=old_password, new_password=new_password
    )

    mock_db = AsyncMock()

    mock_get_user_service.return_value = UserModel(
        id=user_id, email=user_email, hashed_password=old_password_hashed
    )

    mock_verify_password.return_value = True

    mock_hash_password.return_value = "hashed-new-alex's"

    mock_db_update_password.return_value = None

    result = await change_password_service(mock_db, change_password_req, user_email)

    assert isinstance(result, UserModel)
    assert result.id == user_id
    assert result.email == user_email
    assert result.hashed_password == "hashed-new-alex's"


@pytest.mark.asyncio
@patch("app.service.user.verify_password")
@patch("app.service.user.get_user_service")
async def test_change_password_service_failure(
    mock_get_user_service, mock_verify_password
):
    user_email = "addi@addi.com"
    old_password = "old-alex's"
    new_password = "new-alex's"

    change_password_req = ChangePasswordReq(
        old_password=old_password, new_password=new_password
    )

    mock_db = AsyncMock()

    mock_get_user_service.return_value = UserModel(
        id="1", email=user_email, hashed_password="hashed-" + old_password
    )

    mock_verify_password.return_value = False

    with pytest.raises(ValueError) as exc_info:
        await change_password_service(mock_db, change_password_req, user_email)

    assert str(exc_info.value) == "Old password is incorrect"
