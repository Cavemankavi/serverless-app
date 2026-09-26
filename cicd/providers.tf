provider "aws" {
  region = "ap-southeast-1"

  default_tags {
    tags = {
      Project   = "serverless-app"
      ManagedBy = "Terraform"
      Purpose   = "CI/CD"
    }
  }
}