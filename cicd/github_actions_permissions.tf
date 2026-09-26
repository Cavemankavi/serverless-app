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

data "aws_iam_policy_document" "github_actions_deployment" {

  statement {
    sid    = "ManageApplicationInfrastructure"
    effect = "Allow"

    actions = [
      "lambda:*",
      "dynamodb:*",
      "apigateway:*",
      "cognito-idp:*",
      "logs:*",
      "cloudfront:*"
    ]

    resources = ["*"]
  }

  statement {
    sid    = "ManageApplicationS3"
    effect = "Allow"

    actions = [
      "s3:*"
    ]

    resources = [
      "arn:aws:s3:::kaviyan-serverless-app-frontend-dev",
      "arn:aws:s3:::kaviyan-serverless-app-frontend-dev/*"
    ]
  }

  statement {
    sid    = "ManageApplicationIAM"
    effect = "Allow"

    actions = [
      "iam:GetRole",
      "iam:CreateRole",
      "iam:DeleteRole",
      "iam:UpdateAssumeRolePolicy",
      "iam:TagRole",
      "iam:UntagRole",
      "iam:ListRolePolicies",
      "iam:ListAttachedRolePolicies",
      "iam:GetRolePolicy",
      "iam:PutRolePolicy",
      "iam:DeleteRolePolicy",
      "iam:AttachRolePolicy",
      "iam:DetachRolePolicy",
      "iam:PassRole"
    ]

    resources = [
      "arn:aws:iam::621203632375:role/serverless-app-*"
    ]
  }
}

resource "aws_iam_role_policy" "github_actions_deployment" {
  name   = "application-deployment"
  role   = aws_iam_role.github_actions.id
  policy = data.aws_iam_policy_document.github_actions_deployment.json
}

resource "aws_iam_role_policy" "github_actions_state" {
  name   = "terraform-state-access"
  role   = aws_iam_role.github_actions.id
  policy = data.aws_iam_policy_document.github_actions_state.json
}