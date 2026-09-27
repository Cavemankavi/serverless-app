resource "aws_dynamodb_table" "tasks" {
  name         = "serverless-app-tasks-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"

  hash_key = "task_id"

  attribute {
    name = "task_id"
    type = "S"
  }
}

resource "aws_dynamodb_table" "tasks_v2" {
  name         = "serverless-app-tasks-v2-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"

  hash_key  = "owner_id"
  range_key = "task_id"

  attribute {
    name = "owner_id"
    type = "S"
  }

  attribute {
    name = "task_id"
    type = "S"
  }

  attribute {
    name = "list_sort_key"
    type = "S"
  }

  global_secondary_index {
    name            = "user-task-order-index"
    hash_key        = "owner_id"
    range_key       = "list_sort_key"
    projection_type = "ALL"
  }
}
