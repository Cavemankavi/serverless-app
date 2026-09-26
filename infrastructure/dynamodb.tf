resource "aws_dynamodb_table" "tasks" {
  name         = "serverless-app-tasks-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"

  hash_key = "task_id"

  attribute {
    name = "task_id"
    type = "S"
  }
}