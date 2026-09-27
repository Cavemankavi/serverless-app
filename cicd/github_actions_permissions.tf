data "aws_iam_policy_document" "github_plan_state" {

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
    sid    = "ReadWriteTerraformLock"
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject"
    ]

    resources = [
      "arn:aws:s3:::kaviyan-tf-state/serverless-app/terraform.tfstate.tflock"
    ]
  }

  statement {
    sid    = "ReadTerraformState"
    effect = "Allow"

    actions = [
      "s3:GetObject"
    ]

    resources = [
      "arn:aws:s3:::kaviyan-tf-state/serverless-app/terraform.tfstate"
    ]
  }
}

data "aws_iam_policy_document" "github_plan_read" {

  statement {
    sid    = "ReadApplicationInfrastructure"
    effect = "Allow"

    actions = [
      "lambda:Get*",
      "lambda:List*",

      "dynamodb:Describe*",
      "dynamodb:List*",

      "apigateway:GET",

      "cognito-idp:Describe*",
      "cognito-idp:Get*",
      "cognito-idp:List*",

      "logs:Describe*",
      "logs:Get*",
      "logs:List*",

      "cloudfront:Get*",
      "cloudfront:List*",

      "iam:Get*",
      "iam:List*",

      "s3:Get*",
      "s3:List*"
    ]

    resources = ["*"]
  }
}


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

resource "aws_iam_role_policy" "github_plan_state" {
  name   = "terraform-state-access"
  role   = aws_iam_role.github_plan.id
  policy = data.aws_iam_policy_document.github_plan_state.json
}

resource "aws_iam_role_policy" "github_plan_read" {
  name   = "application-read-access"
  role   = aws_iam_role.github_plan.id
  policy = data.aws_iam_policy_document.github_plan_read.json
}

resource "aws_iam_role_policy" "github_actions_state" {
  name   = "terraform-state-access"
  role   = aws_iam_role.github_actions.id
  policy = data.aws_iam_policy_document.github_actions_state.json
}

resource "aws_iam_role_policy" "github_actions_deployment" {
  name   = "application-deployment"
  role   = aws_iam_role.github_actions.id
  policy = data.aws_iam_policy_document.github_actions_deployment.json
}