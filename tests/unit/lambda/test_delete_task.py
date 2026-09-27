import json
from unittest.mock import Mock

from botocore.exceptions import ClientError

import delete_task


def client_error(code):
    return ClientError({"Error": {"Code": code, "Message": "test error"}}, "DeleteItem")


def test_delete_task_deletes_existing_task(monkeypatch):
    table = Mock()
    monkeypatch.setattr(delete_task, "table", table)

    response = delete_task.lambda_handler(
        {"pathParameters": {"id": "task-1"}}, None
    )

    assert response == {"statusCode": 204}
    table.delete_item.assert_called_once_with(
        Key={"task_id": "task-1"},
        ConditionExpression="attribute_exists(task_id)",
    )


def test_delete_task_returns_404_when_task_is_absent(monkeypatch):
    table = Mock()
    table.delete_item.side_effect = client_error("ConditionalCheckFailedException")
    monkeypatch.setattr(delete_task, "table", table)

    response = delete_task.lambda_handler(
        {"pathParameters": {"id": "missing"}}, None
    )

    assert response["statusCode"] == 404
    assert response["headers"] == {"Content-Type": "application/json"}
    assert json.loads(response["body"]) == {"message": "Task not found"}


def test_delete_task_returns_500_for_other_dynamodb_errors(monkeypatch):
    table = Mock()
    table.delete_item.side_effect = client_error("InternalServerError")
    monkeypatch.setattr(delete_task, "table", table)

    response = delete_task.lambda_handler(
        {"pathParameters": {"id": "task-1"}}, None
    )

    assert response["statusCode"] == 500
    assert response["headers"] == {"Content-Type": "application/json"}
    assert json.loads(response["body"]) == {"message": "Internal server error"}
