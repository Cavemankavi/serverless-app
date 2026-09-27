import os
import sys
from pathlib import Path

import pytest
from botocore.endpoint import Endpoint


LAMBDA_SOURCE = Path(__file__).resolve().parents[1] / "src" / "lambda"
sys.path.insert(0, str(LAMBDA_SOURCE))

# Keep boto3 initialization deterministic and prevent credential metadata lookups.
os.environ["TABLE_NAME"] = "unit-test-tasks"
os.environ["TASK_ORDER_INDEX_NAME"] = "user-task-order-index"
os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_SESSION_TOKEN"] = "testing"
os.environ["AWS_EC2_METADATA_DISABLED"] = "true"


@pytest.fixture(autouse=True)
def block_aws_network_calls(monkeypatch):
    def fail_if_called(*args, **kwargs):
        raise RuntimeError("AWS network calls are blocked during unit tests")

    monkeypatch.setattr(Endpoint, "_send", fail_if_called)


@pytest.fixture
def authenticated_event():
    def build(owner_id="user-a", **event_values):
        event = {
            "requestContext": {
                "authorizer": {"jwt": {"claims": {"sub": owner_id}}}
            }
        }
        event.update(event_values)
        return event

    return build
