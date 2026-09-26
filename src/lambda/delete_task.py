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

    logger.info("Received delete task request")

    task_id = event["pathParameters"]["id"]

    try:
        table.delete_item(
            Key={
                "task_id": task_id
            },
            ConditionExpression="attribute_exists(task_id)"
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

        logger.exception("Failed to delete task from DynamoDB")

        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Internal server error"
            })
        }

    logger.info("Task deleted successfully: %s", task_id)

    return {
        "statusCode": 204
    }