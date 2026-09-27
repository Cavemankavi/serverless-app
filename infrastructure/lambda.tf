data "archive_file" "task_handlers" {
  type = "zip"

  source_dir  = "${path.module}/../src/lambda"
  output_path = "${path.module}/task_handlers.zip"
  excludes    = ["__pycache__", "*.pyc"]
}

locals {
  lambda_environment = {
    TABLE_NAME            = aws_dynamodb_table.tasks_v2.name
    TASK_ORDER_INDEX_NAME = "user-task-order-index"
  }
}

resource "aws_lambda_function" "create_task" {
  function_name = "serverless-app-create-task-${var.environment}"

  role    = aws_iam_role.lambda_execution.arn
  handler = "create_task.lambda_handler"
  runtime = "python3.13"

  filename         = data.archive_file.task_handlers.output_path
  source_code_hash = data.archive_file.task_handlers.output_base64sha256

  environment {
    variables = local.lambda_environment
  }
}

resource "aws_lambda_function" "list_tasks" {
  function_name = "serverless-app-list-tasks-${var.environment}"

  role    = aws_iam_role.lambda_execution.arn
  handler = "list_tasks.lambda_handler"
  runtime = "python3.13"

  filename         = data.archive_file.task_handlers.output_path
  source_code_hash = data.archive_file.task_handlers.output_base64sha256

  environment {
    variables = local.lambda_environment
  }
}

resource "aws_lambda_function" "get_task" {
  function_name = "serverless-app-get-task-${var.environment}"

  role    = aws_iam_role.lambda_execution.arn
  handler = "get_task.lambda_handler"
  runtime = "python3.13"

  filename         = data.archive_file.task_handlers.output_path
  source_code_hash = data.archive_file.task_handlers.output_base64sha256

  environment {
    variables = local.lambda_environment
  }
}

resource "aws_lambda_function" "update_task" {
  function_name = "serverless-app-update-task-${var.environment}"

  role    = aws_iam_role.lambda_execution.arn
  handler = "update_task.lambda_handler"
  runtime = "python3.13"

  filename         = data.archive_file.task_handlers.output_path
  source_code_hash = data.archive_file.task_handlers.output_base64sha256

  environment {
    variables = local.lambda_environment
  }
}

resource "aws_lambda_function" "delete_task" {
  function_name = "serverless-app-delete-task-${var.environment}"

  role    = aws_iam_role.lambda_execution.arn
  handler = "delete_task.lambda_handler"
  runtime = "python3.13"

  filename         = data.archive_file.task_handlers.output_path
  source_code_hash = data.archive_file.task_handlers.output_base64sha256

  environment {
    variables = local.lambda_environment
  }
}
