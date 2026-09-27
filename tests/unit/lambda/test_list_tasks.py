import json
from unittest.mock import Mock

import list_tasks


def test_list_tasks_returns_scanned_items(monkeypatch):
    tasks = [{"task_id": "task-1", "title": "Test", "completed": False}]
    table = Mock()
    table.scan.return_value = {"Items": tasks}
    monkeypatch.setattr(list_tasks, "table", table)

    response = list_tasks.lambda_handler({}, None)

    assert response["statusCode"] == 200
    assert response["headers"] == {"Content-Type": "application/json"}
    assert json.loads(response["body"]) == tasks
    table.scan.assert_called_once_with()


def test_list_tasks_returns_empty_list_when_items_are_absent(monkeypatch):
    table = Mock()
    table.scan.return_value = {}
    monkeypatch.setattr(list_tasks, "table", table)

    response = list_tasks.lambda_handler({}, None)

    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == []


def test_list_tasks_returns_500_when_dynamodb_fails(monkeypatch):
    table = Mock()
    table.scan.side_effect = RuntimeError("DynamoDB unavailable")
    monkeypatch.setattr(list_tasks, "table", table)

    response = list_tasks.lambda_handler({}, None)

    assert response["statusCode"] == 500
    assert response["headers"] == {"Content-Type": "application/json"}
    assert json.loads(response["body"]) == {"message": "Internal server error"}
