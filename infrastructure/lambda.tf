data "archive_file" "create_task" {
  type = "zip"

  source_file = "${path.module}/../src/lambda/create_task.py"
  output_path = "${path.module}/create_task.zip"
}

resource "aws_lambda_function" "create_task" {
  function_name = "serverless-app-create-task-${var.environment}"

  role    = aws_iam_role.lambda_execution.arn
  handler = "create_task.lambda_handler"
  runtime = "python3.13"

  filename         = data.archive_file.create_task.output_path
  source_code_hash = data.archive_file.create_task.output_base64sha256

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.tasks.name
    }
  }
}

data "archive_file" "list_tasks" {
  type = "zip"

  source_file = "${path.module}/../src/lambda/list_tasks.py"
  output_path = "${path.module}/list_tasks.zip"
}

resource "aws_lambda_function" "list_tasks" {
  function_name = "serverless-app-list-tasks-${var.environment}"

  role    = aws_iam_role.lambda_execution.arn
  handler = "list_tasks.lambda_handler"
  runtime = "python3.13"

  filename         = data.archive_file.list_tasks.output_path
  source_code_hash = data.archive_file.list_tasks.output_base64sha256

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.tasks.name
    }
  }
}

data "archive_file" "get_task" {
  type = "zip"

  source_file = "${path.module}/../src/lambda/get_task.py"
  output_path = "${path.module}/get_task.zip"
}

resource "aws_lambda_function" "get_task" {
  function_name = "serverless-app-get-task-${var.environment}"

  role    = aws_iam_role.lambda_execution.arn
  handler = "get_task.lambda_handler"
  runtime = "python3.13"

  filename         = data.archive_file.get_task.output_path
  source_code_hash = data.archive_file.get_task.output_base64sha256

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.tasks.name
    }
  }
}

data "archive_file" "update_task" {
  type = "zip"

  source_file = "${path.module}/../src/lambda/update_task.py"
  output_path = "${path.module}/update_task.zip"
}

resource "aws_lambda_function" "update_task" {
  function_name = "serverless-app-update-task-${var.environment}"

  role    = aws_iam_role.lambda_execution.arn
  handler = "update_task.lambda_handler"
  runtime = "python3.13"

  filename         = data.archive_file.update_task.output_path
  source_code_hash = data.archive_file.update_task.output_base64sha256

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.tasks.name
    }
  }
}

data "archive_file" "delete_task" {
  type = "zip"

  source_file = "${path.module}/../src/lambda/delete_task.py"
  output_path = "${path.module}/delete_task.zip"
}

resource "aws_lambda_function" "delete_task" {
  function_name = "serverless-app-delete-task-${var.environment}"

  role    = aws_iam_role.lambda_execution.arn
  handler = "delete_task.lambda_handler"
  runtime = "python3.13"

  filename         = data.archive_file.delete_task.output_path
  source_code_hash = data.archive_file.delete_task.output_base64sha256

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.tasks.name
    }
  }
}