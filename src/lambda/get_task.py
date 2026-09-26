import json
import logging
import os

import boto3


logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):

    logger.info("Received get task request")

    task_id = event["pathParameters"]["id"]

    try:
        response = table.get_item(
            Key={
                "task_id": task_id
            }
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
        "body": json.dumps(task)
    }