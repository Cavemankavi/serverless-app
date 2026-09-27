import pytest

import list_tasks


def test_aws_network_calls_are_blocked():
    with pytest.raises(
        RuntimeError, match="AWS network calls are blocked during unit tests"
    ):
        list_tasks.table.scan()
