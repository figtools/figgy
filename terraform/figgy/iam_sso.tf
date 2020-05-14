# Only necessary if you are planning to use Figgy's SSO integration with OKTA
# If you already use SSO for OKTA, you probably don't need to do this and can avoid provisioning this user

resource "aws_iam_saml_provider" "okta" {
  count = local.enable_sso == true && local.sso_type == "okta" ? 1 : 0
  name                   = "OKTA"
  saml_metadata_document = file("saml/metadata-okta.xml")
}

resource "aws_iam_user" "sso_user" {
  count = local.enable_sso == true && local.sso_type == "okta" ? 1 : 0
  name = "figgy-OktaSSOUser"
  path = "/system/"

  tags = {
    created_by = "figgy"
  }
}

resource "aws_iam_user_policy_attachment" "okta_attachment" {
  count = local.enable_sso == true && local.sso_type == "okta" ? 1 : 0
  policy_arn = aws_iam_policy.okta_policy[count.index].arn
  user = aws_iam_user.sso_user[count.index].name
}

# SSO List roles poliy
resource "aws_iam_policy" "okta_policy" {
  count = local.enable_sso == true && local.sso_type == "okta" ? 1 : 0
  name = "okta-list-roles"
  path = "/system/"
  description = "This policy enables OKTA to list roles available for OKTA -> AWS SSO integration"
  policy = data.aws_iam_policy_document.sso_list[count.index].json
}

data "aws_iam_policy_document" "sso_list" {
  count = local.enable_sso == true && local.sso_type == "okta" ? 1 : 0
  statement {
    sid = "OktaSSOListRoles"
    actions = [
        "iam:ListRoles",
        "iam:ListAccountAliases"
    ]

    resources = ["*"]
  }
}

# Be careful if you change this name, it is used by SSO integrations. When we retrieve the SAML assertion from our SSO provider,
# the role ARNs provide us the accountId -> run_env -> role mapping that is necessary for Figgy to operate properly.
# The name format MUST be something-${var.run_env}-${role_type} - you MAY replace 'figgy' with anything else you like.
resource "aws_iam_role" "sso_user_role" {
  count = local.enable_sso == true && local.sso_type == "okta" ? length(local.role_types) : 0
  name                 = "figgy-${var.run_env}-${local.role_types[count.index]}"
  assume_role_policy   = local.enable_sso == true && local.sso_type == "okta" ? data.aws_iam_policy_document.sso_role_policy[0].json : ""
  max_session_duration = var.max_session_duration
}

# SSO SAML sts policy
data "aws_iam_policy_document" "sso_role_policy" {
  count = local.enable_sso == true && local.sso_type == "okta" ? 1 : 0
  statement {
    effect = "Allow"

    principals {
      identifiers = [ aws_iam_saml_provider.okta[0].arn ]
      type        = "Federated"
    }

    actions = [
      "sts:AssumeRoleWithSAML",
    ]

    condition {
      test     = "StringEquals"
      variable = "SAML:aud"
      values   = ["https://signin.aws.amazon.com/saml"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "figgy_access_policy_attachment" {
  count = local.enable_sso == true && local.sso_type == "okta" ? length(local.role_types) : 0
  role = aws_iam_role.sso_user_role[count.index].name
  policy_arn = aws_iam_policy.figgy_access_policy[count.index].arn
}
