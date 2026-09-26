import json
import logging
import os
import uuid
from datetime import datetime, timezone

import boto3


logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):

    logger.info("Received create task request")

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

    task = {
        "task_id": str(uuid.uuid4()),
        "title": title.strip(),
        "completed": False,
        "created_at": datetime.now(timezone.utc).isoformat()
    }

    try:
        table.put_item(Item=task)
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
        "body": json.dumps(task)
    }