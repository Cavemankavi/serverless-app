import json
from unittest.mock import Mock

import get_task


def test_get_task_returns_existing_task(monkeypatch):
    task = {"task_id": "task-1", "title": "Test", "completed": False}
    table = Mock()
    table.get_item.return_value = {"Item": task}
    monkeypatch.setattr(get_task, "table", table)

    response = get_task.lambda_handler({"pathParameters": {"id": "task-1"}}, None)

    assert response["statusCode"] == 200
    assert response["headers"] == {"Content-Type": "application/json"}
    assert json.loads(response["body"]) == task
    table.get_item.assert_called_once_with(Key={"task_id": "task-1"})


def test_get_task_returns_404_when_task_is_absent(monkeypatch):
    table = Mock()
    table.get_item.return_value = {}
    monkeypatch.setattr(get_task, "table", table)

    response = get_task.lambda_handler({"pathParameters": {"id": "missing"}}, None)

    assert response["statusCode"] == 404
    assert response["headers"] == {"Content-Type": "application/json"}
    assert json.loads(response["body"]) == {"message": "Task not found"}


def test_get_task_returns_500_when_dynamodb_fails(monkeypatch):
    table = Mock()
    table.get_item.side_effect = RuntimeError("DynamoDB unavailable")
    monkeypatch.setattr(get_task, "table", table)

    response = get_task.lambda_handler({"pathParameters": {"id": "task-1"}}, None)

    assert response["statusCode"] == 500
    assert response["headers"] == {"Content-Type": "application/json"}
    assert json.loads(response["body"]) == {"message": "Internal server error"}
