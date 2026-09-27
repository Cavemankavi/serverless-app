import json
import logging
import os

import boto3
from boto3.dynamodb.conditions import Key

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
task_order_index_name = os.environ["TASK_ORDER_INDEX_NAME"]


def lambda_handler(event, context):

    logger.info("Received list tasks request")

    try:
        owner_id = get_authenticated_owner_id(event)
    except UnauthorizedError:
        logger.warning("Request lacked an authenticated user identity")
        return unauthorized_response()

    try:
        query_arguments = {
            "IndexName": task_order_index_name,
            "KeyConditionExpression": Key("owner_id").eq(owner_id),
            "ScanIndexForward": True,
        }
        tasks = []

        while True:
            response = table.query(**query_arguments)
            tasks.extend(response.get("Items", []))

            last_evaluated_key = response.get("LastEvaluatedKey")
            if not last_evaluated_key:
                break

            query_arguments["ExclusiveStartKey"] = last_evaluated_key
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

    logger.info("Successfully retrieved %d tasks", len(tasks))

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps([public_task(task) for task in tasks])
    }
