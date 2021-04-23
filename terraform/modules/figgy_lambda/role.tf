
data "aws_caller_identity" "current" {}

data "aws_region" "current" {}


locals {
  role_name = var.lambda_name
  role_arn = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.lambda_name}"
}

resource "aws_iam_role" "figgy_role" {
  count = var.create_role ? 1 : 0
  name = local.role_name
  assume_role_policy = data.aws_iam_policy_document.assume_policy[0].json

  # Prevents TF from always detecting changes in the name even when there are none, causing resource recreation.
//  lifecycle {
//    ignore_changes = [name]
//  }
}

# If creating role, attach policies AFTER role creation.
resource "aws_iam_role_policy_attachment" "role_policy_attachment_on_create" {
  count      = var.create_role ? length(var.policies) : 0
  role       = aws_iam_role.figgy_role[0].arn
  policy_arn = var.policies[count.index]
}

# If role exists, attach policies to role.
resource "aws_iam_role_policy_attachment" "role_policy_attachment_on_existing" {
  count      = var.create_role ?  0 : length(var.policies)
  role       = local.role_arn
  policy_arn = var.policies[count.index]
}

data "aws_iam_policy_document" "assume_policy" {
  count = var.create_role ? 1 : 0
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}