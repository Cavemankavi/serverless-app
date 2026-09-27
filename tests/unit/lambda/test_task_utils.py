from datetime import datetime, timezone

import pytest

from task_utils import build_list_sort_key, get_authenticated_owner_id


def test_order_keys_sort_by_completion_then_newest_then_task_id():
    older = datetime(2026, 9, 27, 1, tzinfo=timezone.utc)
    newer = datetime(2026, 9, 27, 2, tzinfo=timezone.utc)
    keys = [
        build_list_sort_key(True, newer, "task-b"),
        build_list_sort_key(False, older, "task-a"),
        build_list_sort_key(False, newer, "task-b"),
        build_list_sort_key(True, older, "task-a"),
    ]
    assert sorted(keys) == [keys[2], keys[1], keys[0], keys[3]]


def test_order_key_uses_task_id_as_deterministic_tie_breaker():
    created_at = datetime(2026, 9, 27, 1, tzinfo=timezone.utc)
    assert build_list_sort_key(False, created_at, "task-a") < build_list_sort_key(
        False, created_at, "task-b"
    )


def test_order_key_requires_timezone():
    with pytest.raises(ValueError, match="timezone"):
        build_list_sort_key(False, datetime(2026, 9, 27), "task-a")


@pytest.mark.parametrize(
    "event",
    [
        {},
        {"requestContext": None},
        {"requestContext": {"authorizer": {"jwt": {"claims": {}}}}},
        {"requestContext": {"authorizer": {"jwt": {"claims": {"sub": ""}}}}},
    ],
)
def test_authenticated_owner_requires_non_empty_sub(event):
    with pytest.raises(ValueError, match="identity"):
        get_authenticated_owner_id(event)
