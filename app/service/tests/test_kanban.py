from unittest.mock import AsyncMock, patch

import pytest

from app.schemas.kanban import (AddKanbanItemReq, KanbanCreateReq,
                                RemoveKanbanItemReq)
from app.service.kanban import (add_kanban_item_service, create_kanban_service,
                                delete_kanban_item_service)


@pytest.mark.asyncio
@patch("app.service.kanban.db_add_kanban_to_team")
@patch("app.service.kanban.db_create_kanban")
async def test_create_kanban_service_success(
    mock_db_create_kanban, mock_db_add_kanban_to_team
):
    kanban_id = "1"
    kanban_name = "addi's kanban"
    team_id = "alex's_team_id"
    kanban_create_req = KanbanCreateReq(name=kanban_name, team_id=team_id)

    mock_db = AsyncMock()

    mock_db_create_kanban.return_value = {
        "_id": kanban_id,
        "name": kanban_name,
    }
    mock_db_add_kanban_to_team.return_value = None

    result = await create_kanban_service(mock_db, kanban_create_req)

    assert result.id == kanban_id
    assert result.name == kanban_name
    mock_db_create_kanban.assert_called_once_with(mock_db, kanban_create_req)
    mock_db_add_kanban_to_team.assert_called_once_with(mock_db, team_id, kanban_id)


@pytest.mark.asyncio
@patch("app.service.kanban.db_create_kanban")
async def test_create_kanban_service_failure(mock_db_create_kanban):
    kanban_name = "addi's kanban"
    team_id = "alex's_team_id"
    kanban_create_req = KanbanCreateReq(name=kanban_name, team_id=team_id)

    mock_db = AsyncMock()

    mock_db_create_kanban.side_effect = Exception("Database error")

    with pytest.raises(Exception) as exc_info:
        await create_kanban_service(mock_db, kanban_create_req)

    assert str(exc_info.value) == "Database error"


@pytest.mark.asyncio
@patch("app.service.kanban.db_add_kanban_item")
async def test_add_kanban_item_service_success(mock_db_add_kanban_item):
    kanban_id = "1"
    item_id = "addi's_item_id"
    item_name = "alex's task"
    start_at = 1234567890.0
    end_at = 1234567900.0
    column = 1
    owner = "addi@addi.com"

    add_kanban_item_req = AddKanbanItemReq(
        name=item_name,
        start_at=start_at,
        end_at=end_at,
        column=column,
        owner=owner,
    )

    mock_db = AsyncMock()

    mock_db_add_kanban_item.return_value = {
        "_id": item_id,
        "name": item_name,
        "start_at": start_at,
        "end_at": end_at,
        "column": column,
        "owner": owner,
    }

    result = await add_kanban_item_service(mock_db, kanban_id, add_kanban_item_req)

    assert result.id == item_id
    assert result.name == item_name
    assert result.start_at == start_at
    assert result.end_at == end_at
    assert result.column == column
    assert result.owner == owner


@pytest.mark.asyncio
@patch("app.service.kanban.db_add_kanban_item")
async def test_add_kanban_item_service_failure(mock_db_add_kanban_item):
    kanban_id = "1"
    item_name = "alex's task"
    start_at = 1234567890.0
    end_at = 1234567900.0
    column = 1
    owner = "addi@addi.com"

    add_kanban_item_req = AddKanbanItemReq(
        name=item_name,
        start_at=start_at,
        end_at=end_at,
        column=column,
        owner=owner,
    )

    mock_db = AsyncMock()

    mock_db_add_kanban_item.side_effect = Exception("Database error")

    with pytest.raises(Exception) as exc_info:
        await add_kanban_item_service(mock_db, kanban_id, add_kanban_item_req)

    assert str(exc_info.value) == "Database error"


@pytest.mark.asyncio
@patch("app.service.kanban.db_remove_kanban_item")
async def test_delete_kanban_item_service_success(mock_db_remove_kanban_item):
    kanban_id = "1"
    item_id = "addi's_item_id"

    remove_kanban_item_req = RemoveKanbanItemReq(item_id=item_id)

    mock_db = AsyncMock()

    mock_db_remove_kanban_item.return_value = None

    await delete_kanban_item_service(mock_db, kanban_id, remove_kanban_item_req)

    mock_db_remove_kanban_item.assert_called_once_with(mock_db, kanban_id, item_id)


@pytest.mark.asyncio
@patch("app.service.kanban.db_remove_kanban_item")
async def test_delete_kanban_item_service_failure(mock_db_remove_kanban_item):
    kanban_id = "1"
    item_id = "addi's_item_id"

    remove_kanban_item_req = RemoveKanbanItemReq(item_id=item_id)

    mock_db = AsyncMock()

    mock_db_remove_kanban_item.side_effect = Exception("Database error")

    with pytest.raises(Exception) as exc_info:
        await delete_kanban_item_service(mock_db, kanban_id, remove_kanban_item_req)

    assert str(exc_info.value) == "Database error"
