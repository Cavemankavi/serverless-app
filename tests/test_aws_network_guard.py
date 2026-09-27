import pytest

import list_tasks


def test_aws_network_calls_are_blocked():
    with pytest.raises(
        RuntimeError, match="AWS network calls are blocked during unit tests"
    ):
        list_tasks.table.query(
            IndexName="user-task-order-index",
            KeyConditionExpression="owner_id = :owner_id",
            ExpressionAttributeValues={":owner_id": "user-a"},
        )
