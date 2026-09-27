output "dynamodb_table_name" {
  description = "Name of the DynamoDB tasks table"
  value       = aws_dynamodb_table.tasks_v2.name
}

output "dynamodb_table_arn" {
  description = "ARN of the DynamoDB tasks table"
  value       = aws_dynamodb_table.tasks_v2.arn
}

output "api_url" {
  description = "Base URL of the HTTP API"
  value       = aws_apigatewayv2_api.main.api_endpoint
}

output "frontend_url" {
  description = "CloudFront URL for the frontend"
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "cognito_user_pool_id" {
  description = "Cognito User Pool ID"
  value       = aws_cognito_user_pool.main.id
}

output "cognito_client_id" {
  description = "Cognito frontend application client ID"
  value       = aws_cognito_user_pool_client.frontend.id
}

output "cognito_domain" {
  description = "Cognito managed login domain"
  value       = aws_cognito_user_pool_domain.main.domain
}

output "cloudfront_distribution_id" {
  description = "CloudFront distribution ID"
  value       = aws_cloudfront_distribution.frontend.id
}
