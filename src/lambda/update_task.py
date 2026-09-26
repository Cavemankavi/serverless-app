import json
import logging
import os

import boto3
from botocore.exceptions import ClientError


logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):

    logger.info("Received update task request")

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

    try:
        response = table.update_item(
            Key={
                "task_id": task_id
            },
            UpdateExpression="SET completed = :completed",
            ExpressionAttributeValues={
                ":completed": completed
            },
            ConditionExpression="attribute_exists(task_id)",
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
        "body": json.dumps(response["Attributes"])
    }