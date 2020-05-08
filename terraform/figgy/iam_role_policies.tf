locals {
  global_read_namespaces = ["/shared", "/figgy"]
}

# Be careful if you change this name, it is used by SSO integrations. When we retrieve the SAML assertion from our SSO provider,
# the role ARNs provide us the accountId -> run_env -> role mapping that is necessary for Figgy to operate properly.
# The name format MUST be something-${var.run_env}-${role_type} - you MAY replace 'figgy' with anything else you like.
resource "aws_iam_role" "sso_user_role" {
  count = length(local.role_types)
  name                 = "figgy-${var.run_env}-${local.role_types[count.index]}"
  assume_role_policy   = local.enable_sso == true && local.sso_type == "okta" ? data.aws_iam_policy_document.sso_role_policy.json : ""
  max_session_duration = var.max_session_duration
}

# SSO SAML sts policy
data "aws_iam_policy_document" "sso_role_policy" {
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

# Policy created by
resource "aws_iam_policy" "figgy_access_policy" {
  count = length(local.role_types)
  name        = "figgy_${local.role_types[count.index]}_access"
  description = "Dynamic figgy access policy for role: ${local.role_types[count.index]}"
  policy      = data.aws_iam_policy_document.dynamic_policy[count.index].json
}

resource "aws_iam_role_policy_attachment" "figgy_access_policy_attachment" {
  count = length(local.role_types)
  role = aws_iam_role.sso_user_role[count.index].name
  policy_arn = aws_iam_policy.figgy_access_policy[count.index].arn
}


# Dynamically assembled policy based on configure_figgy.tf locals configurations
data "aws_iam_policy_document" "dynamic_policy" {
  count = length(local.role_types)
  statement {
    sid = "KmsDecryptPermissions"
    actions = [
      "kms:DescribeKey",
      "kms:Decrypt"
    ]
    resources = [
      # Looks up the keys the role has access to, then looks up the ARN from the provisioned key for that type
      for key_name in local.role_to_kms_access[local.role_types[count.index]]:
        aws_kms_key.encryption_key[index(local.encryption_keys, key_name)].arn
    ]
  }

  statement {
    sid = "KmsEncryptPermissions"
    actions = [ "kms:Encrypt" ]
    resources = [
      # Looks up the keys the role has access to, then looks up the ARN from the provisioned key for that type
      for key_name in local.role_to_kms_access[local.role_types[count.index]]:
        aws_kms_key.encryption_key[index(local.encryption_keys, key_name)].arn
    ]
  }

  statement {
    sid = "ListKeys"
    actions = [ "kms:ListKeys" ]
    resources = [ "*" ]
  }

  statement {
    sid = "ParameterStorePermissions"
    actions = [
      "ssm:DeleteParameter",
      "ssm:DeleteParameters",
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:GetParameterHistory",
      "ssm:GetParametersByPath",
      "ssm:PutParameter"
    ]

    # EVERYONE gets access to /shared, it is our global namespace.
    resources = concat([
      for ns in local.role_to_ns_access[local.role_types[count.index]]:
        "arn:aws:ssm:*:${data.aws_caller_identity.current.account_id}:parameter${ns}/*"
      ], [
        for ns in local.global_read_namespaces:
          "arn:aws:ssm:*:${data.aws_caller_identity.current.account_id}:parameter${ns}/*"
      ]
    )
  }
  
  statement {
    sid = "PSDescribe"
    actions = [ "ssm:DescribeParameters" ]
    resources = [ "*" ]
  }
  
  statement {
    sid = "ConfigReplAccess"
    actions = [
      "dynamodb:Get*",
      "dynamodb:List*",
      "dynamodb:Put*",
      "dynamodb:Delete*",
      "dynamodb:Query",
      "dynamodb:Scan",
      "dynamodb:UpdateItem",
      "dynamodb:UpdateTimeToLive"
    ]
    resources = [ aws_dynamodb_table.config_replication.arn ]
  }
  
  statement {
    sid = "ReadFiggyDDBTables"
    actions = [
      "dynamodb:Get*",
      "dynamodb:List*",
      "dynamodb:Query",
      "dynamodb:Scan" 
    ]
    
    resources = [
      aws_dynamodb_table.config_replication.arn,
      aws_dynamodb_table.config_auditor.arn,
      aws_dynamodb_table.config_cache.arn
    ]
  }
  
}