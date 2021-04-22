
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

# Then parse through the list using count
resource "aws_iam_role_policy_attachment" "role_policy_attachment" {
  count      = var.create_role ? length(var.policies) : 0
  role       = aws_iam_role.figgy_role[0].name
  policy_arn = var.policies[count.index]
  depends_on = [aws_iam_role.figgy_role]
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