import json
import logging
import os
import uuid
from datetime import datetime, timezone

import boto3

from task_utils import (
    UnauthorizedError,
    build_list_sort_key,
    get_authenticated_owner_id,
    public_task,
    unauthorized_response,
)


logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):

    logger.info("Received create task request")

    try:
        owner_id = get_authenticated_owner_id(event)
    except UnauthorizedError:
        logger.warning("Request lacked an authenticated user identity")
        return unauthorized_response()

    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        logger.warning("Request contained invalid JSON")

        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Request body must contain valid JSON"
            })
        }

    title = body.get("title")

    if not isinstance(title, str) or not title.strip():
        logger.warning("Request rejected because title was missing or invalid")

        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "title must be a non-empty string"
            })
        }

    task_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc)

    task = {
        "owner_id": owner_id,
        "task_id": task_id,
        "title": title.strip(),
        "completed": False,
        "created_at": created_at.isoformat(),
        "list_sort_key": build_list_sort_key(False, created_at, task_id),
    }

    try:
        table.put_item(
            Item=task,
            ConditionExpression=(
                "attribute_not_exists(owner_id) AND attribute_not_exists(task_id)"
            ),
        )
    except Exception:
        logger.exception("Failed to write task to DynamoDB")

        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Internal server error"
            })
        }

    logger.info("Task created successfully: %s", task["task_id"])

    return {
        "statusCode": 201,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(public_task(task))
    }
