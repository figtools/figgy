


# Used to provide generic figgy access to its utilities. Does not provide access to any secrets, keys, or environments.
# All users of figgy should have this role
resource "aws_iam_role" "default_role" {
  count                = var.cfgs.utility_account_id == var.aws_account_id ? 1 : 0
  name                 = "figgy-default"
  assume_role_policy   = var.cfgs.enable_sso ? data.aws_iam_policy_document.sso_role_policy[0].json : null
  max_session_duration = var.max_session_duration
}


resource "aws_iam_role_policy_attachment" "figgy_ots_policy_attachment" {
  count      = var.cfgs.utility_account_id == var.aws_account_id ? 1 : 0
  role       = aws_iam_role.default_role[count.index].name
  policy_arn = aws_iam_policy.figgy_ots_policy[count.index].arn
}
