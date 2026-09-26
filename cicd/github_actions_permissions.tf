data "aws_iam_policy_document" "github_actions_state" {

  statement {
    sid    = "ListTerraformState"
    effect = "Allow"

    actions = [
      "s3:ListBucket"
    ]

    resources = [
      "arn:aws:s3:::kaviyan-tf-state"
    ]

    condition {
      test     = "StringLike"
      variable = "s3:prefix"

      values = [
        "serverless-app/terraform.tfstate",
        "serverless-app/terraform.tfstate.tflock"
      ]
    }
  }

  statement {
    sid    = "ReadWriteTerraformState"
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject"
    ]

    resources = [
      "arn:aws:s3:::kaviyan-tf-state/serverless-app/terraform.tfstate",
      "arn:aws:s3:::kaviyan-tf-state/serverless-app/terraform.tfstate.tflock"
    ]
  }
}

resource "aws_iam_role_policy" "github_actions_state" {
  name   = "terraform-state-access"
  role   = aws_iam_role.github_actions.id
  policy = data.aws_iam_policy_document.github_actions_state.json
}