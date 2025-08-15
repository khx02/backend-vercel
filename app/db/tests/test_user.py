from unittest.mock import AsyncMock
import pytest

from app.db.user import create_user, get_user_by_email, update_password
from app.schemas.user import UserHashed


@pytest.mark.asyncio
async def test_create_user_success():
    user_hashed = UserHashed(email="addi@addi.com", hashed_password="hashed-alex's")

    mock_collection = AsyncMock()
    mock_result = AsyncMock()
    mock_result.inserted_id = "some-unique-id"
    mock_collection.insert_one.return_value = mock_result

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    result = await create_user(mock_db, user_hashed)

    mock_collection.insert_one.assert_called_once_with(
        {
            "email": user_hashed.email,
            "hashed_password": user_hashed.hashed_password,
            "_id": "some-unique-id",
        }
    )
    assert result["_id"] == "some-unique-id"
    assert result["email"] == user_hashed.email
    assert result["hashed_password"] == user_hashed.hashed_password


@pytest.mark.asyncio
async def test_create_user_failure():
    user_hashed = UserHashed(email="addi@addi.com", hashed_password="hashed-alex's")

    mock_collection = AsyncMock()
    mock_collection.insert_one.side_effect = Exception("Database error")

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    result = await create_user(mock_db, user_hashed)

    assert result is None


@pytest.mark.asyncio
async def test_get_user_by_email_success():
    user_id = "1"
    user_email = "addi@addi.com"
    user_hashed_password = "hashed-alex's"

    mock_collection = AsyncMock()
    mock_collection.find_one.return_value = {
        "_id": user_id,
        "email": user_email,
        "hashed_password": user_hashed_password,
    }

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    result = await get_user_by_email(mock_db, user_email)

    assert result["_id"] == user_id
    assert result["email"] == user_email
    assert result["hashed_password"] == user_hashed_password


@pytest.mark.asyncio
async def test_get_user_by_email_failure():
    user_email = "addi@addi.com"

    mock_collection = AsyncMock()
    mock_collection.find_one.side_effect = Exception("Database error")

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    result = await get_user_by_email(mock_db, user_email)

    assert result is None


@pytest.mark.asyncio
async def test_update_password_success():
    mock_collection = AsyncMock()
    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    result = await update_password(mock_db, "addi@addi.com", "new-hashed-password")

    mock_collection.update_one.assert_called_once_with(
        {"email": "addi@addi.com"},
        {"$set": {"hashed_password": "new-hashed-password"}},
    )
    assert result is None


@pytest.mark.asyncio
async def test_update_password_failure():
    mock_collection = AsyncMock()
    mock_collection.update_one.side_effect = Exception("Database error")

    mock_db = AsyncMock()
    mock_db.__getitem__.return_value = mock_collection

    with pytest.raises(Exception) as exc_info:
        await update_password(mock_db, "addi@addi.com", "new-hashed-password")

    mock_collection.update_one.assert_called_once_with(
        {"email": "addi@addi.com"},
        {"$set": {"hashed_password": "new-hashed-password"}},
    )
    assert str(exc_info.value) == "Database error"
