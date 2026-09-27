import json
from unittest.mock import Mock, call

from boto3.dynamodb.conditions import Key

import list_tasks


def task(task_id, completed=False):
    return {
        "owner_id": "user-a",
        "task_id": task_id,
        "title": task_id,
        "completed": completed,
        "created_at": "2026-09-27T01:00:00+00:00",
        "list_sort_key": f"{int(completed)}#9999999999999999#{task_id}",
    }


def test_list_tasks_queries_only_authenticated_owner_and_hides_internal_fields(
    monkeypatch, authenticated_event
):
    ordered_tasks = [task("new-incomplete"), task("old-incomplete"), task("done", True)]
    table = Mock()
    table.query.return_value = {"Items": ordered_tasks}
    monkeypatch.setattr(list_tasks, "table", table)

    response = list_tasks.lambda_handler(authenticated_event(), None)

    assert response["statusCode"] == 200
    returned_tasks = json.loads(response["body"])
    assert [item["task_id"] for item in returned_tasks] == [
        "new-incomplete",
        "old-incomplete",
        "done",
    ]
    assert all("owner_id" not in item for item in returned_tasks)
    assert all("list_sort_key" not in item for item in returned_tasks)
    table.query.assert_called_once_with(
        IndexName="user-task-order-index",
        KeyConditionExpression=Key("owner_id").eq("user-a"),
        ScanIndexForward=True,
    )
    table.scan.assert_not_called()


def test_list_tasks_follows_query_pagination_in_order(monkeypatch, authenticated_event):
    page_key = {
        "owner_id": "user-a",
        "task_id": "task-2",
        "list_sort_key": "0#2#task-2",
    }
    table = Mock()
    table.query.side_effect = [
        {"Items": [task("task-1"), task("task-2")], "LastEvaluatedKey": page_key},
        {"Items": [task("task-3", True)]},
    ]
    monkeypatch.setattr(list_tasks, "table", table)

    response = list_tasks.lambda_handler(authenticated_event(), None)

    assert [item["task_id"] for item in json.loads(response["body"])] == [
        "task-1",
        "task-2",
        "task-3",
    ]
    condition = Key("owner_id").eq("user-a")
    assert table.query.call_args_list == [
        call(
            IndexName="user-task-order-index",
            KeyConditionExpression=condition,
            ScanIndexForward=True,
        ),
        call(
            IndexName="user-task-order-index",
            KeyConditionExpression=condition,
            ScanIndexForward=True,
            ExclusiveStartKey=page_key,
        ),
    ]


def test_list_tasks_returns_empty_list(monkeypatch, authenticated_event):
    table = Mock()
    table.query.return_value = {}
    monkeypatch.setattr(list_tasks, "table", table)
    response = list_tasks.lambda_handler(authenticated_event(), None)
    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == []


def test_list_tasks_rejects_missing_authenticated_identity(monkeypatch):
    table = Mock()
    monkeypatch.setattr(list_tasks, "table", table)
    response = list_tasks.lambda_handler({}, None)
    assert response["statusCode"] == 401
    table.query.assert_not_called()


def test_list_tasks_returns_500_when_dynamodb_fails(
    monkeypatch, authenticated_event
):
    table = Mock()
    table.query.side_effect = RuntimeError("DynamoDB unavailable")
    monkeypatch.setattr(list_tasks, "table", table)
    response = list_tasks.lambda_handler(authenticated_event(), None)
    assert response["statusCode"] == 500
    assert json.loads(response["body"]) == {"message": "Internal server error"}
