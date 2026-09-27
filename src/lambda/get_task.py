import json
import logging
import os

import boto3

from task_utils import (
    UnauthorizedError,
    get_authenticated_owner_id,
    public_task,
    unauthorized_response,
)


logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):

    logger.info("Received get task request")

    try:
        owner_id = get_authenticated_owner_id(event)
    except UnauthorizedError:
        logger.warning("Request lacked an authenticated user identity")
        return unauthorized_response()

    task_id = event["pathParameters"]["id"]

    try:
        response = table.get_item(
            Key={
                "owner_id": owner_id,
                "task_id": task_id
            },
            ConsistentRead=True,
        )
    except Exception:
        logger.exception("Failed to retrieve task from DynamoDB")

        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Internal server error"
            })
        }

    task = response.get("Item")

    if not task:
        logger.warning("Task not found: %s", task_id)

        return {
            "statusCode": 404,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Task not found"
            })
        }

    logger.info("Task retrieved successfully: %s", task_id)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(public_task(task))
    }
