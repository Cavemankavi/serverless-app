output "github_actions_role_arn" {
  description = "IAM role assumed by GitHub Actions"
  value       = aws_iam_role.github_actions.arn
}