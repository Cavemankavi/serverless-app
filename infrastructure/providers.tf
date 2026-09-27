provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "serverless-app"
      Environment = var.environment
      ManagedBy   = "Terraform"
      Deployment  = "GitHubActions"
    }
  }
}