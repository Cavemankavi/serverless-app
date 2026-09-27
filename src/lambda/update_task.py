import json
import logging
import os

import boto3
from botocore.exceptions import ClientError

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

    logger.info("Received update task request")

    try:
        owner_id = get_authenticated_owner_id(event)
    except UnauthorizedError:
        logger.warning("Request lacked an authenticated user identity")
        return unauthorized_response()

    task_id = event["pathParameters"]["id"]

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

    completed = body.get("completed")

    if not isinstance(completed, bool):
        logger.warning("Request rejected because completed was missing or invalid")

        return {
            "statusCode": 400,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "completed must be a boolean"
            })
        }

    key = {
        "owner_id": owner_id,
        "task_id": task_id,
    }

    try:
        existing_task = table.get_item(Key=key, ConsistentRead=True).get("Item")

        if not existing_task:
            logger.warning("Task not found: %s", task_id)
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"message": "Task not found"}),
            }

        if existing_task["completed"] == completed:
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(public_task(existing_task)),
            }

        list_sort_key = build_list_sort_key(
            completed, existing_task["created_at"], task_id
        )

        response = table.update_item(
            Key=key,
            UpdateExpression=(
                "SET completed = :completed, list_sort_key = :list_sort_key"
            ),
            ExpressionAttributeValues={
                ":completed": completed,
                ":list_sort_key": list_sort_key,
                ":created_at": existing_task["created_at"],
            },
            ConditionExpression=(
                "attribute_exists(owner_id) AND attribute_exists(task_id) "
                "AND created_at = :created_at"
            ),
            ReturnValues="ALL_NEW"
        )

    except ClientError as error:

        if error.response["Error"]["Code"] == "ConditionalCheckFailedException":
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

        logger.exception("Failed to update task in DynamoDB")

        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Internal server error"
            })
        }

    logger.info("Task updated successfully: %s", task_id)

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(public_task(response["Attributes"]))
    }
