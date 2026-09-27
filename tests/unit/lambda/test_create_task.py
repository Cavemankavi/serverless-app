import json
from datetime import datetime
from unittest.mock import Mock
from uuid import UUID

import pytest

import create_task


def test_create_task_stores_and_returns_a_new_task(monkeypatch):
    table = Mock()
    monkeypatch.setattr(create_task, "table", table)

    response = create_task.lambda_handler(
        {"body": json.dumps({"title": "  Write tests  "})}, None
    )

    assert response["statusCode"] == 201
    assert response["headers"] == {"Content-Type": "application/json"}

    task = json.loads(response["body"])
    assert task["title"] == "Write tests"
    assert task["completed"] is False
    assert UUID(task["task_id"])
    assert datetime.fromisoformat(task["created_at"]).utcoffset().total_seconds() == 0
    table.put_item.assert_called_once_with(Item=task)


def test_create_task_rejects_invalid_json(monkeypatch):
    table = Mock()
    monkeypatch.setattr(create_task, "table", table)

    response = create_task.lambda_handler({"body": "{"}, None)

    assert response["statusCode"] == 400
    assert response["headers"] == {"Content-Type": "application/json"}
    assert json.loads(response["body"]) == {
        "message": "Request body must contain valid JSON"
    }
    table.put_item.assert_not_called()


@pytest.mark.parametrize(
    "body",
    [
        {},
        {"title": None},
        {"title": 123},
        {"title": ""},
        {"title": "   "},
    ],
)
def test_create_task_rejects_invalid_titles(monkeypatch, body):
    table = Mock()
    monkeypatch.setattr(create_task, "table", table)

    response = create_task.lambda_handler({"body": json.dumps(body)}, None)

    assert response["statusCode"] == 400
    assert response["headers"] == {"Content-Type": "application/json"}
    assert json.loads(response["body"]) == {
        "message": "title must be a non-empty string"
    }
    table.put_item.assert_not_called()


def test_create_task_returns_500_when_dynamodb_fails(monkeypatch):
    table = Mock()
    table.put_item.side_effect = RuntimeError("DynamoDB unavailable")
    monkeypatch.setattr(create_task, "table", table)

    response = create_task.lambda_handler(
        {"body": json.dumps({"title": "Write tests"})}, None
    )

    assert response["statusCode"] == 500
    assert response["headers"] == {"Content-Type": "application/json"}
    assert json.loads(response["body"]) == {"message": "Internal server error"}
