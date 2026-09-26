resource "aws_cloudwatch_log_group" "create_task" {
  name              = "/aws/lambda/${aws_lambda_function.create_task.function_name}"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "list_tasks" {
  name              = "/aws/lambda/${aws_lambda_function.list_tasks.function_name}"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "get_task" {
  name              = "/aws/lambda/${aws_lambda_function.get_task.function_name}"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "update_task" {
  name              = "/aws/lambda/${aws_lambda_function.update_task.function_name}"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "delete_task" {
  name              = "/aws/lambda/${aws_lambda_function.delete_task.function_name}"
  retention_in_days = 14
}

resource "aws_cloudwatch_log_group" "api_gateway" {
  name              = "/aws/apigateway/serverless-app-${var.environment}"
  retention_in_days = 14
}