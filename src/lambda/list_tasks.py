import json
import logging
import os

import boto3


logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):

    logger.info("Received list tasks request")

    try:
        response = table.scan()
    except Exception:
        logger.exception("Failed to retrieve tasks from DynamoDB")

        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "message": "Internal server error"
            })
        }

    tasks = response.get("Items", [])

    logger.info("Successfully retrieved %d tasks", len(tasks))

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(tasks)
    }