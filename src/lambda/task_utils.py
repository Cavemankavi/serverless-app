import calendar
from datetime import datetime


MAX_TIMESTAMP_MICROSECONDS = 9_999_999_999_999_999
PUBLIC_TASK_FIELDS = ("task_id", "title", "completed", "created_at")


class UnauthorizedError(ValueError):
    pass


def get_authenticated_owner_id(event):
    try:
        owner_id = event["requestContext"]["authorizer"]["jwt"]["claims"]["sub"]
    except (KeyError, TypeError):
        raise UnauthorizedError("Authenticated user identity is missing") from None

    if not isinstance(owner_id, str) or not owner_id:
        raise UnauthorizedError("Authenticated user identity is missing")

    return owner_id


def build_list_sort_key(completed, created_at, task_id):
    if isinstance(created_at, str):
        created_at = datetime.fromisoformat(created_at)

    if created_at.utcoffset() is None:
        raise ValueError("created_at must include a timezone")

    timestamp_microseconds = (
        calendar.timegm(created_at.utctimetuple()) * 1_000_000
        + created_at.microsecond
    )
    reverse_timestamp = MAX_TIMESTAMP_MICROSECONDS - timestamp_microseconds

    if reverse_timestamp < 0:
        raise ValueError("created_at is outside the supported range")

    completion_rank = "1" if completed else "0"
    return f"{completion_rank}#{reverse_timestamp:016d}#{task_id}"


def public_task(task):
    return {field: task[field] for field in PUBLIC_TASK_FIELDS}


def unauthorized_response():
    return {
        "statusCode": 401,
        "headers": {"Content-Type": "application/json"},
        "body": '{"message": "Unauthorized"}',
    }
