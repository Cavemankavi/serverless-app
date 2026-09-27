import json
from unittest.mock import Mock

import pytest
from botocore.exceptions import ClientError

import update_task


CREATED_AT = "2026-09-27T01:02:03.456789+00:00"


def stored_task(completed=False, owner_id="user-a"):
    rank = int(completed)
    return {
        "owner_id": owner_id,
        "task_id": "task-1",
        "title": "Test",
        "completed": completed,
        "created_at": CREATED_AT,
        "list_sort_key": f"{rank}#8242509476543211#task-1",
    }


def client_error(code):
    return ClientError({"Error": {"Code": code, "Message": "test error"}}, "UpdateItem")


@pytest.mark.parametrize(
    ("before", "after", "expected_prefix"),
    [(False, True, "1#"), (True, False, "0#")],
)
def test_update_task_moves_index_entry_without_changing_created_at(
    monkeypatch, authenticated_event, before, after, expected_prefix
):
    original = stored_task(before)
    updated = {**original, "completed": after}
    table = Mock()
    table.get_item.return_value = {"Item": original}
    table.update_item.return_value = {"Attributes": updated}
    monkeypatch.setattr(update_task, "table", table)

    response = update_task.lambda_handler(
        authenticated_event(
            pathParameters={"id": "task-1"},
            body=json.dumps({"completed": after, "owner_id": "user-b"}),
        ),
        None,
    )

    assert response["statusCode"] == 200
    returned_task = json.loads(response["body"])
    assert returned_task["created_at"] == CREATED_AT
    assert "owner_id" not in returned_task
    assert "list_sort_key" not in returned_task
    table.get_item.assert_called_once_with(
        Key={"owner_id": "user-a", "task_id": "task-1"}, ConsistentRead=True
    )
    update_call = table.update_item.call_args.kwargs
    assert update_call["Key"] == {"owner_id": "user-a", "task_id": "task-1"}
    assert update_call["ExpressionAttributeValues"][":list_sort_key"].startswith(
        expected_prefix
    )
    assert update_call["ExpressionAttributeValues"][":created_at"] == CREATED_AT
    assert "created_at" not in update_call["UpdateExpression"]


def test_update_task_skips_write_when_state_is_unchanged(
    monkeypatch, authenticated_event
):
    original = stored_task(True)
    table = Mock()
    table.get_item.return_value = {"Item": original}
    monkeypatch.setattr(update_task, "table", table)
    response = update_task.lambda_handler(
        authenticated_event(
            pathParameters={"id": "task-1"},
            body=json.dumps({"completed": True}),
        ),
        None,
    )
    assert response["statusCode"] == 200
    assert json.loads(response["body"])["created_at"] == CREATED_AT
    table.update_item.assert_not_called()


def test_update_task_returns_404_for_foreign_or_missing_task(
    monkeypatch, authenticated_event
):
    table = Mock()
    table.get_item.return_value = {}
    monkeypatch.setattr(update_task, "table", table)
    response = update_task.lambda_handler(
        authenticated_event(
            "user-b",
            pathParameters={"id": "task-1"},
            body=json.dumps({"completed": True}),
        ),
        None,
    )
    assert response["statusCode"] == 404
    assert table.get_item.call_args.kwargs["Key"] == {
        "owner_id": "user-b",
        "task_id": "task-1",
    }
    table.update_item.assert_not_called()


def test_update_task_maps_conditional_failure_to_404(
    monkeypatch, authenticated_event
):
    table = Mock()
    table.get_item.return_value = {"Item": stored_task(False)}
    table.update_item.side_effect = client_error("ConditionalCheckFailedException")
    monkeypatch.setattr(update_task, "table", table)
    response = update_task.lambda_handler(
        authenticated_event(
            pathParameters={"id": "task-1"},
            body=json.dumps({"completed": True}),
        ),
        None,
    )
    assert response["statusCode"] == 404


def test_update_task_rejects_invalid_json(monkeypatch, authenticated_event):
    table = Mock()
    monkeypatch.setattr(update_task, "table", table)
    response = update_task.lambda_handler(
        authenticated_event(pathParameters={"id": "task-1"}, body="{"), None
    )
    assert response["statusCode"] == 400
    table.get_item.assert_not_called()


@pytest.mark.parametrize("completed", [None, 0, 1, "true", [], {}])
def test_update_task_rejects_non_boolean_values(
    monkeypatch, authenticated_event, completed
):
    table = Mock()
    monkeypatch.setattr(update_task, "table", table)
    response = update_task.lambda_handler(
        authenticated_event(
            pathParameters={"id": "task-1"},
            body=json.dumps({"completed": completed}),
        ),
        None,
    )
    assert response["statusCode"] == 400
    table.get_item.assert_not_called()


def test_update_task_rejects_missing_authenticated_identity(monkeypatch):
    table = Mock()
    monkeypatch.setattr(update_task, "table", table)
    response = update_task.lambda_handler(
        {"pathParameters": {"id": "task-1"}, "body": '{"completed": true}'},
        None,
    )
    assert response["statusCode"] == 401
    table.get_item.assert_not_called()


def test_update_task_returns_500_for_dynamodb_error(
    monkeypatch, authenticated_event
):
    table = Mock()
    table.get_item.side_effect = client_error("InternalServerError")
    monkeypatch.setattr(update_task, "table", table)
    response = update_task.lambda_handler(
        authenticated_event(
            pathParameters={"id": "task-1"},
            body=json.dumps({"completed": True}),
        ),
        None,
    )
    assert response["statusCode"] == 500
