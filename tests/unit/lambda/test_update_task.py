import json
from unittest.mock import Mock

import pytest
from botocore.exceptions import ClientError

import update_task


def client_error(code):
    return ClientError({"Error": {"Code": code, "Message": "test error"}}, "UpdateItem")


@pytest.mark.parametrize("completed", [True, False])
def test_update_task_updates_and_returns_task(monkeypatch, completed):
    task = {"task_id": "task-1", "title": "Test", "completed": completed}
    table = Mock()
    table.update_item.return_value = {"Attributes": task}
    monkeypatch.setattr(update_task, "table", table)

    response = update_task.lambda_handler(
        {
            "pathParameters": {"id": "task-1"},
            "body": json.dumps({"completed": completed}),
        },
        None,
    )

    assert response["statusCode"] == 200
    assert response["headers"] == {"Content-Type": "application/json"}
    assert json.loads(response["body"]) == task
    table.update_item.assert_called_once_with(
        Key={"task_id": "task-1"},
        UpdateExpression="SET completed = :completed",
        ExpressionAttributeValues={":completed": completed},
        ConditionExpression="attribute_exists(task_id)",
        ReturnValues="ALL_NEW",
    )


def test_update_task_rejects_invalid_json(monkeypatch):
    table = Mock()
    monkeypatch.setattr(update_task, "table", table)

    response = update_task.lambda_handler(
        {"pathParameters": {"id": "task-1"}, "body": "{"}, None
    )

    assert response["statusCode"] == 400
    assert response["headers"] == {"Content-Type": "application/json"}
    assert json.loads(response["body"]) == {
        "message": "Request body must contain valid JSON"
    }
    table.update_item.assert_not_called()


@pytest.mark.parametrize("completed", [None, 0, 1, "true", [], {}])
def test_update_task_rejects_non_boolean_completed_values(monkeypatch, completed):
    table = Mock()
    monkeypatch.setattr(update_task, "table", table)

    response = update_task.lambda_handler(
        {
            "pathParameters": {"id": "task-1"},
            "body": json.dumps({"completed": completed}),
        },
        None,
    )

    assert response["statusCode"] == 400
    assert response["headers"] == {"Content-Type": "application/json"}
    assert json.loads(response["body"]) == {"message": "completed must be a boolean"}
    table.update_item.assert_not_called()


def test_update_task_returns_404_when_task_is_absent(monkeypatch):
    table = Mock()
    table.update_item.side_effect = client_error("ConditionalCheckFailedException")
    monkeypatch.setattr(update_task, "table", table)

    response = update_task.lambda_handler(
        {
            "pathParameters": {"id": "missing"},
            "body": json.dumps({"completed": True}),
        },
        None,
    )

    assert response["statusCode"] == 404
    assert response["headers"] == {"Content-Type": "application/json"}
    assert json.loads(response["body"]) == {"message": "Task not found"}


def test_update_task_returns_500_for_other_dynamodb_errors(monkeypatch):
    table = Mock()
    table.update_item.side_effect = client_error("InternalServerError")
    monkeypatch.setattr(update_task, "table", table)

    response = update_task.lambda_handler(
        {
            "pathParameters": {"id": "task-1"},
            "body": json.dumps({"completed": True}),
        },
        None,
    )

    assert response["statusCode"] == 500
    assert response["headers"] == {"Content-Type": "application/json"}
    assert json.loads(response["body"]) == {"message": "Internal server error"}
