import json
from unittest.mock import Mock

from botocore.exceptions import ClientError

import delete_task


def client_error(code):
    return ClientError({"Error": {"Code": code, "Message": "test error"}}, "DeleteItem")


def test_delete_task_uses_owner_scoped_key(monkeypatch, authenticated_event):
    table = Mock()
    monkeypatch.setattr(delete_task, "table", table)
    response = delete_task.lambda_handler(
        authenticated_event(pathParameters={"id": "task-1"}), None
    )
    assert response == {"statusCode": 204}
    table.delete_item.assert_called_once_with(
        Key={"owner_id": "user-a", "task_id": "task-1"},
        ConditionExpression=(
            "attribute_exists(owner_id) AND attribute_exists(task_id)"
        ),
    )


def test_delete_task_returns_404_for_foreign_or_missing_task(
    monkeypatch, authenticated_event
):
    table = Mock()
    table.delete_item.side_effect = client_error("ConditionalCheckFailedException")
    monkeypatch.setattr(delete_task, "table", table)
    response = delete_task.lambda_handler(
        authenticated_event("user-b", pathParameters={"id": "task-1"}), None
    )
    assert response["statusCode"] == 404
    assert json.loads(response["body"]) == {"message": "Task not found"}
    assert table.delete_item.call_args.kwargs["Key"] == {
        "owner_id": "user-b",
        "task_id": "task-1",
    }


def test_delete_task_rejects_missing_authenticated_identity(monkeypatch):
    table = Mock()
    monkeypatch.setattr(delete_task, "table", table)
    response = delete_task.lambda_handler(
        {"pathParameters": {"id": "task-1"}}, None
    )
    assert response["statusCode"] == 401
    table.delete_item.assert_not_called()


def test_delete_task_returns_500_for_other_dynamodb_errors(
    monkeypatch, authenticated_event
):
    table = Mock()
    table.delete_item.side_effect = client_error("InternalServerError")
    monkeypatch.setattr(delete_task, "table", table)
    response = delete_task.lambda_handler(
        authenticated_event(pathParameters={"id": "task-1"}), None
    )
    assert response["statusCode"] == 500
    assert json.loads(response["body"]) == {"message": "Internal server error"}
