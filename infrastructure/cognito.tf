resource "aws_cognito_user_pool" "main" {
  name = "serverless-app-users-${var.environment}"

  username_attributes = [
    "email"
  ]

  auto_verified_attributes = [
    "email"
  ]

  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }
}

resource "aws_cognito_user_pool_client" "frontend" {
  name = "serverless-app-frontend-${var.environment}"

  user_pool_id = aws_cognito_user_pool.main.id

  generate_secret = false

  explicit_auth_flows = [
    "ALLOW_USER_SRP_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH"
  ]

  allowed_oauth_flows = [
    "code"
  ]

  allowed_oauth_scopes = [
    "openid",
    "email",
    "profile"
  ]

  allowed_oauth_flows_user_pool_client = true

  supported_identity_providers = [
    "COGNITO"
  ]

  callback_urls = [
    "http://localhost:8000",
    "https://${aws_cloudfront_distribution.frontend.domain_name}"
  ]

  logout_urls = [
    "http://localhost:8000",
    "https://${aws_cloudfront_distribution.frontend.domain_name}"
  ]
}

resource "aws_cognito_user_pool_domain" "main" {
  domain       = "kaviyan-serverless-app-${var.environment}"
  user_pool_id = aws_cognito_user_pool.main.id
}

