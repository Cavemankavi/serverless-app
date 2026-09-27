import json
from datetime import datetime
from unittest.mock import Mock
from uuid import UUID

import pytest

import create_task


def test_create_task_stores_owned_task_and_hides_internal_fields(
    monkeypatch, authenticated_event
):
    table = Mock()
    monkeypatch.setattr(create_task, "table", table)

    response = create_task.lambda_handler(
        authenticated_event(
            body=json.dumps(
                {"title": "  Write tests  ", "owner_id": "attacker-controlled"}
            )
        ),
        None,
    )

    assert response["statusCode"] == 201
    task = json.loads(response["body"])
    assert task["title"] == "Write tests"
    assert task["completed"] is False
    assert "owner_id" not in task
    assert "list_sort_key" not in task
    assert UUID(task["task_id"])
    assert datetime.fromisoformat(task["created_at"]).utcoffset().total_seconds() == 0

    stored_task = table.put_item.call_args.kwargs["Item"]
    assert stored_task["owner_id"] == "user-a"
    assert stored_task["list_sort_key"].startswith("0#")
    assert all(stored_task[field] == value for field, value in task.items())
    assert table.put_item.call_args.kwargs["ConditionExpression"] == (
        "attribute_not_exists(owner_id) AND attribute_not_exists(task_id)"
    )


def test_create_task_rejects_missing_authenticated_identity(monkeypatch):
    table = Mock()
    monkeypatch.setattr(create_task, "table", table)
    response = create_task.lambda_handler(
        {"body": json.dumps({"title": "Write tests"})}, None
    )
    assert response["statusCode"] == 401
    assert json.loads(response["body"]) == {"message": "Unauthorized"}
    table.put_item.assert_not_called()


def test_create_task_rejects_invalid_json(monkeypatch, authenticated_event):
    table = Mock()
    monkeypatch.setattr(create_task, "table", table)
    response = create_task.lambda_handler(authenticated_event(body="{"), None)
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {
        "message": "Request body must contain valid JSON"
    }
    table.put_item.assert_not_called()


@pytest.mark.parametrize(
    "body", [{}, {"title": None}, {"title": 123}, {"title": ""}, {"title": "   "}]
)
def test_create_task_rejects_invalid_titles(monkeypatch, authenticated_event, body):
    table = Mock()
    monkeypatch.setattr(create_task, "table", table)
    response = create_task.lambda_handler(
        authenticated_event(body=json.dumps(body)), None
    )
    assert response["statusCode"] == 400
    assert json.loads(response["body"]) == {
        "message": "title must be a non-empty string"
    }
    table.put_item.assert_not_called()


def test_create_task_returns_500_when_dynamodb_fails(
    monkeypatch, authenticated_event
):
    table = Mock()
    table.put_item.side_effect = RuntimeError("DynamoDB unavailable")
    monkeypatch.setattr(create_task, "table", table)
    response = create_task.lambda_handler(
        authenticated_event(body=json.dumps({"title": "Write tests"})), None
    )
    assert response["statusCode"] == 500
    assert json.loads(response["body"]) == {"message": "Internal server error"}
