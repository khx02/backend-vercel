from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException, status

from app.api.kanban import add_kanban_item, create_kanban, remove_kanban_item
from app.schemas.kanban import (AddKanbanItemReq, KanbanCreateReq, KanbanItem,
                                KanbanModel, RemoveKanbanItemReq)


@pytest.mark.asyncio
@patch("app.api.kanban.create_kanban_service")
async def test_create_kanban_success(mock_create_kanban_service):
    mock_db = AsyncMock()

    team_id = "team-1"
    mock_kanban_name = "Test Kanban"
    kanban_create_req = KanbanCreateReq(name=mock_kanban_name, team_id=team_id)

    mock_create_kanban_service.return_value = KanbanModel(
        id="kanban-1",
        name=mock_kanban_name,
        kanban_elements=[],
    )

    result = await create_kanban(kanban_create_req, mock_db)

    assert result.id == "kanban-1"
    assert result.name == mock_kanban_name
    assert result.kanban_elements == []


@pytest.mark.asyncio
@patch("app.api.kanban.create_kanban_service")
async def test_create_kanban_failure(mock_create_kanban_service):
    mock_db = AsyncMock()

    team_id = "team-1"
    mock_kanban_name = "Test Kanban"
    kanban_create_req = KanbanCreateReq(name=mock_kanban_name, team_id=team_id)

    mock_create_kanban_service.side_effect = Exception("Database error")

    with pytest.raises(HTTPException) as exc_info:
        await create_kanban(kanban_create_req, mock_db)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc_info.value.detail == "Failed to create kanban board"


@pytest.mark.asyncio
@patch("app.api.kanban.add_kanban_item_service")
async def test_add_kanban_item_success(mock_add_kanban_item_service):
    mock_db = AsyncMock()

    kanban_id = "kanban-1"
    add_item_req = AddKanbanItemReq(
        name="Test Item",
        start_at=1234567890.0,
        end_at=1234567900.0,
        column=1,
        owner="addi@addi.com",
    )

    mock_kanban_item = KanbanItem(
        id="item-1",
        name="Test Item",
        start_at=1234567890.0,
        end_at=1234567900.0,
        column=1,
        owner="addi@addi.com",
    )

    mock_add_kanban_item_service.return_value = mock_kanban_item

    result = await add_kanban_item(kanban_id, add_item_req, mock_db)

    assert result.id == "item-1"
    assert result.name == "Test Item"
    assert result.start_at == 1234567890.0
    assert result.end_at == 1234567900.0
    assert result.column == 1
    assert result.owner == "addi@addi.com"
    mock_add_kanban_item_service.assert_called_once_with(
        mock_db, kanban_id, add_item_req
    )


@pytest.mark.asyncio
@patch("app.api.kanban.add_kanban_item_service")
async def test_add_kanban_item_failure(mock_add_kanban_item_service):
    mock_db = AsyncMock()

    kanban_id = "kanban-1"
    add_item_req = AddKanbanItemReq(
        name="Test Item",
        start_at=1234567890.0,
        end_at=1234567900.0,
        column=1,
        owner="addi@addi.com",
    )

    mock_add_kanban_item_service.side_effect = Exception("Database error")

    with pytest.raises(HTTPException) as exc_info:
        await add_kanban_item(kanban_id, add_item_req, mock_db)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc_info.value.detail == "Failed to add item to kanban board"


@pytest.mark.asyncio
@patch("app.api.kanban.delete_kanban_item_service")
async def test_remove_kanban_item_success(mock_delete_kanban_item_service):
    mock_db = AsyncMock()

    kanban_id = "kanban-1"
    remove_item_req = RemoveKanbanItemReq(item_id="item-1")
    mock_delete_kanban_item_service.return_value = None

    result = await remove_kanban_item(kanban_id, remove_item_req, mock_db)

    assert result is None
    mock_delete_kanban_item_service.assert_called_once_with(
        mock_db, kanban_id, remove_item_req
    )


@pytest.mark.asyncio
@patch("app.api.kanban.delete_kanban_item_service")
async def test_remove_kanban_item_failure(mock_delete_kanban_item_service):
    mock_db = AsyncMock()

    kanban_id = "kanban-1"
    remove_item_req = RemoveKanbanItemReq(item_id="item-1")
    mock_delete_kanban_item_service.side_effect = Exception("Database error")

    with pytest.raises(HTTPException) as exc_info:
        await remove_kanban_item(kanban_id, remove_item_req, mock_db)

    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc_info.value.detail == "Failed to remove item from kanban board"
