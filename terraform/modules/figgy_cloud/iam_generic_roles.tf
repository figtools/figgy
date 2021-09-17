


# Used to provide generic figgy access to its utilities. Does not provide access to any secrets, keys, or environments.
# All users of figgy should have this role
resource "aws_iam_role" "default_role" {
  count                = var.cfgs.utility_account_id == var.aws_account_id && var.primary_region ? 1 : 0
  name                 = "figgy-default"
  assume_role_policy   = var.cfgs.enable_sso ? data.aws_iam_policy_document.sso_role_policy[count.index].json : data.aws_iam_policy_document.figgy_bastion_default_role_policy.json
  max_session_duration = var.max_session_duration
}

# Role policy to allow cross-account assumption from bastion account
data "aws_iam_policy_document" "figgy_bastion_default_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"

    principals {
      type = "AWS"

      identifiers = [
        for role in var.cfgs.role_types:
          "arn:aws:iam::${var.cfgs.bastion_account_number}:role/figgy-${role}"
      ]
    }

    dynamic "condition" {
      for_each = var.cfgs.mfa_enabled ? [true] : []
      content {
        test     = "Bool"
        values   = [var.cfgs.mfa_enabled]
        variable = "aws:MultiFactorAuthPresent"
      }
    }
  }
}



resource "aws_iam_role_policy_attachment" "figgy_ots_policy_attachment" {
  count      = var.cfgs.utility_account_id == var.aws_account_id && var.primary_region ? 1 : 0
  role       = aws_iam_role.default_role[count.index].name
  policy_arn = aws_iam_policy.figgy_ots_policy[count.index].arn
}

resource "aws_iam_role_policy_attachment" "figgy_default_policy_attachment" {
  count      = var.cfgs.utility_account_id == var.aws_account_id && var.primary_region ? 1 : 0
  role       = aws_iam_role.default_role[count.index].name
  policy_arn = aws_iam_policy.figgy_default[count.index].arn
}
