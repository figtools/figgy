# This user is required by the okta API integration to do dynamic role lookups in the OKTA Console.
# If you already use SSO for OKTA with AWS, you probably don't need to do this and can avoid provisioning this user

locals {
  okta_enabled = var.cfgs.enable_sso && var.primary_region && contains(var.cfgs.auth_types, "okta")
}

resource "aws_iam_user" "sso_user" {
  count = local.okta_enabled ? 1 : 0
  name  = "figgy-${var.cfgs.auth_type}SSOUser"
  path  = "/system/"

  tags = {
    created_by = "figgy"
  }
}


resource "aws_iam_user_policy_attachment" "okta_attachment" {
  count      = local.okta_enabled  ? 1 : 0
  policy_arn = aws_iam_policy.okta_policy[count.index].arn
  user       = aws_iam_user.sso_user[count.index].name
}

# SSO List roles poliy
resource "aws_iam_policy" "okta_policy" {
  count       = local.okta_enabled  ? 1 : 0
  name        = "${var.cfgs.auth_type}-list-roles"
  path        = "/system/"
  description = "This policy enables OKTA to list roles available for OKTA -> AWS SSO integration"
  policy      = data.aws_iam_policy_document.sso_list[count.index].json
}

data "aws_iam_policy_document" "sso_list" {
  count = local.okta_enabled  ? 1 : 0
  statement {
    sid = "OktaSSOListRoles"
    actions = [
      "iam:ListRoles",
      "iam:ListAccountAliases"
    ]

    resources = ["*"]
  }
}