# Only necessary if you are planning to use Figgy's SSO integration
# Todo - Change this back to just metadata.xml for simplicity sake.
resource "aws_iam_saml_provider" "provider" {
  count = local.enable_sso == true ? 1 : 0
  name                   = local.sso_type
  saml_metadata_document = file("saml/metadata-${local.sso_type}.xml")
}

# Be careful if you change this name, it is used by SSO integrations. When we retrieve the SAML assertion from our SSO provider,
# the role ARNs provide us the accountId -> run_env -> role mapping that is necessary for Figgy to operate properly.
# The name format MUST be something-${var.run_env}-${role_type} - you MAY replace 'figgy' with anything else you like.
resource "aws_iam_role" "sso_user_role" {
  count = local.enable_sso == true ? length(local.role_types) : 0
  name                 = "figgy-${var.run_env}-${local.role_types[count.index]}"
  assume_role_policy   = local.enable_sso == true ? data.aws_iam_policy_document.sso_role_policy[0].json : ""
  max_session_duration = var.max_session_duration
}

# SSO SAML sts policy
data "aws_iam_policy_document" "sso_role_policy" {
  count = local.enable_sso == true ? 1 : 0
  statement {
    effect = "Allow"

    principals {
      identifiers = [ aws_iam_saml_provider.provider[0].arn ]
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
  count = local.enable_sso == true ? length(local.role_types) : 0
  role = aws_iam_role.sso_user_role[count.index].name
  policy_arn = aws_iam_policy.figgy_access_policy[count.index].arn
}
