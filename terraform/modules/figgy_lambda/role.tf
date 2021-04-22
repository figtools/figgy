
data "aws_caller_identity" "current" {
}

locals {
  role_arn = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/${var.lambda_name}"
}

resource "aws_iam_role" "figgy_role" {
  count = var.create_role ? 1 : 0
  name = var.lambda_name
  assume_role_policy = data.aws_iam_policy_document.assume_policy.json
}

# Then parse through the list using count
resource "aws_iam_role_policy_attachment" "role_policy_attachment" {
  role       = aws_iam_role.figgy_role[0].name
  count      = var.create_role ? length(var.policies) : 0
  policy_arn = var.policies[count.index]
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