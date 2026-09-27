import json
from unittest.mock import Mock

import get_task


def stored_task():
    return {
        "owner_id": "user-a",
        "task_id": "task-1",
        "title": "Test",
        "completed": False,
        "created_at": "2026-09-27T01:00:00+00:00",
        "list_sort_key": "0#9999999999999999#task-1",
    }


def test_get_task_uses_owner_scoped_key_and_hides_internal_fields(
    monkeypatch, authenticated_event
):
    table = Mock()
    table.get_item.return_value = {"Item": stored_task()}
    monkeypatch.setattr(get_task, "table", table)
    response = get_task.lambda_handler(
        authenticated_event(pathParameters={"id": "task-1"}), None
    )
    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {
        "task_id": "task-1",
        "title": "Test",
        "completed": False,
        "created_at": "2026-09-27T01:00:00+00:00",
    }
    table.get_item.assert_called_once_with(
        Key={"owner_id": "user-a", "task_id": "task-1"}, ConsistentRead=True
    )


def test_get_task_returns_404_for_foreign_or_missing_task(
    monkeypatch, authenticated_event
):
    table = Mock()
    table.get_item.return_value = {}
    monkeypatch.setattr(get_task, "table", table)
    response = get_task.lambda_handler(
        authenticated_event("user-b", pathParameters={"id": "task-1"}), None
    )
    assert response["statusCode"] == 404
    assert json.loads(response["body"]) == {"message": "Task not found"}
    table.get_item.assert_called_once_with(
        Key={"owner_id": "user-b", "task_id": "task-1"}, ConsistentRead=True
    )


def test_get_task_rejects_missing_authenticated_identity(monkeypatch):
    table = Mock()
    monkeypatch.setattr(get_task, "table", table)
    response = get_task.lambda_handler({"pathParameters": {"id": "task-1"}}, None)
    assert response["statusCode"] == 401
    table.get_item.assert_not_called()


def test_get_task_returns_500_when_dynamodb_fails(monkeypatch, authenticated_event):
    table = Mock()
    table.get_item.side_effect = RuntimeError("DynamoDB unavailable")
    monkeypatch.setattr(get_task, "table", table)
    response = get_task.lambda_handler(
        authenticated_event(pathParameters={"id": "task-1"}), None
    )
    assert response["statusCode"] == 500
    assert json.loads(response["body"]) == {"message": "Internal server error"}
