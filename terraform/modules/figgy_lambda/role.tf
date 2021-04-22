
data "aws_caller_identity" "current" {}

data "aws_region" "current" {}


locals {
  role_arn = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.lambda_name}"
}

resource "aws_iam_role" "figgy_role" {
  name = "${var.lambda_name}-${data.aws_region.current.name}"
  assume_role_policy = data.aws_iam_policy_document.assume_policy.json
}

# Then parse through the list using count
resource "aws_iam_role_policy_attachment" "role_policy_attachment" {
  role       = aws_iam_role.figgy_role.name
  count      = length(var.policies)
  policy_arn = var.policies[count.index]
  depends_on = [aws_iam_role.figgy_role]
}

data "aws_iam_policy_document" "assume_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}