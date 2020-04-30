# Only necessary if you are planning to use Figgy's SSO integration with OKTA
# If you already use SSO for OKTA, you probably don't need to do this and can avoid provisioning this user

# Todo: You will need to provide your own metadata.xml file!
resource "aws_iam_saml_provider" "okta" {
  name                   = "OKTA"
  saml_metadata_document = file("saml/metadata-${var.run_env}.xml")
}

resource "aws_iam_user" "sso_user" {
  name = "figgy-OktaSSOUser"
  path = "/system/"

  tags = {
    created_by = "figgy"
  }
}

resource "aws_iam_user_policy_attachment" "okta_attachment" {
  policy_arn = aws_iam_policy.okta_policy.arn
  user = aws_iam_user.sso_user.name
}

# SSO List roles poliy
resource "aws_iam_policy" "okta_policy" {
  name = "okta-list-roles"
  path = "/system/"
  description = "This policy enables OKTA to list roles available for OKTA -> AWS SSO integration"
  policy = data.aws_iam_policy_document.sso_list.json
}

data "aws_iam_policy_document" "sso_list" {
  statement {
    sid = "OktaSSOListRoles"
    actions = [
        "iam:ListRoles",
        "iam:ListAccountAliases"
    ]

    resources = ["*"]
  }
}
