# Default lambda policy
resource "aws_iam_policy" "lambda_default" {
  count = var.primary_region ? 1 : 0
  name        = local.lambda_default_policy_name
  path        = "/"
  description = "Default IAM policy for figgy lambda. Provides basic Lambda access, such as writing logs to CW."
  policy      = data.aws_iam_policy_document.cloudwatch_logs_write.json

//  # Prevents TF from always detecting changes in the name even when there are none, causing resource recreation.
//  lifecycle {
//    ignore_changes = [name]
//  }
}


# Config Auditor Lambda
resource "aws_iam_policy" "config_auditor" {
  count = var.primary_region ? 1 : 0
  name        = local.config_auditor_name
  path        = "/"
  description = "IAM policy for figgy config-auditor lambda"
  policy      = data.aws_iam_policy_document.config_auditor_document[0].json

//  # Prevents TF from always detecting changes in the name even when there are none, causing resource recreation.
//  lifecycle {
//    ignore_changes = [name]
//  }
}

data "aws_iam_policy_document" "config_auditor_document" {
  count = var.primary_region ? 1 : 0
  statement {
    sid = "AuditTableDDBAccess"
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
    resources = [
      "arn:aws:dynamodb:*:${local.account_id}:table/${aws_dynamodb_table.config_auditor.name}"
    ]
  }

  statement {
    sid = "AuditorPSRead"
    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:List*",
      "ssm:DescribeParameters"
    ]
    resources = ["*"]
  }
}

# Usage Tracker
resource "aws_iam_policy" "config_usage_tracker" {
  count = var.primary_region ? 1 : 0
  name        = local.config_usage_tracker_name
  path        = "/"
  description = "IAM policy for figgy config-usage-tracker lambda"
  policy      = data.aws_iam_policy_document.config_usage_tracker[0].json

//  # Prevents TF from always detecting changes in the name even when there are none, causing resource recreation.
//  lifecycle {
//    ignore_changes = [name]
//  }
}

data "aws_iam_policy_document" "config_usage_tracker" {
  count = var.primary_region ? 1 : 0

  statement {
    sid = "UsageTrackerTableDDBAccess"
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
    resources = [
      "arn:aws:dynamodb:*:${local.account_id}:table/${aws_dynamodb_table.config_usage_tracker.name}",
      "arn:aws:dynamodb:*:${local.account_id}:table/${aws_dynamodb_table.user_cache.name}"
    ]
  }

  statement {
    sid = "UsageTrackerS3Access"
    actions = [
      "s3:GetObject*",
    ]
    resources = [
      "arn:aws:s3:::${aws_s3_bucket.figgy_bucket.id}/*"
    ]
  }
}

resource "aws_iam_policy" "config_usage_tracker_s3" {
  count = var.primary_region ? 1 : 0
  name        = "${local.config_usage_tracker_name}-s3-${data.aws_region.current.name}"
  path        = "/"
  description = "IAM policy for figgy config-usage-tracker lambda in region: ${data.aws_region.current.name}"
  policy      = data.aws_iam_policy_document.config_usage_tracker_s3.id
}


data "aws_iam_policy_document" "config_usage_tracker_s3" {
  statement {
    sid = "UsageTrackerS3Access"
    actions = [
      "s3:GetObject*",
    ]
    resources = [
      "arn:aws:s3:::${aws_s3_bucket.figgy_bucket.id}/*"
    ]
  }
}

# Config cache manager / syncer lambdas
resource "aws_iam_policy" "config_cache_manager" {
  count = var.primary_region ? 1 : 0
  name        = local.config_cache_manager_name
  path        = "/"
  description = "IAM policy for figgy config_cache_manager/syncer lambdas"
  policy      = data.aws_iam_policy_document.config_cache_manager_document[0].json

//  # Prevents TF from always detecting changes in the name even when there are none, causing resource recreation.
//  lifecycle {
//    ignore_changes = [name]
//  }
}

data "aws_iam_policy_document" "config_cache_manager_document" {
  count = var.primary_region ? 1 : 0

  statement {
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
    resources = ["arn:aws:dynamodb:*:${local.account_id}:table/${aws_dynamodb_table.config_cache.name}"]
  }

  statement {
    sid       = "SSMDescribe"
    actions   = ["ssm:DescribeParameters"]
    resources = ["*"]
  }
}

# KMS Decrypt by Region Policy
resource "aws_iam_policy" "kms_decrypt" {
  name        = "${local.kms_decrypt_policy_name}-${local.region}"
  path        = "/"
  description = "IAM policy for lambdas to decrypt configurations."
  policy      = data.aws_iam_policy_document.figgy_kms_document.json

//  # Prevents TF from always detecting changes in the name even when there are none, causing resource recreation.
  lifecycle {
    ignore_changes = [name]
  }
}

data "aws_iam_policy_document" "figgy_kms_document" {
  provider = aws.region

  statement {
    sid = "FiggyKMSAccess"
    actions = [
      "kms:DescribeKey",
      "kms:Decrypt",
      "kms:Encrypt"
    ]

    resources = concat([for x in aws_kms_key.encryption_key : x.arn], [aws_kms_key.replication_key.arn])
  }
}

# Replication lambdas policy
resource "aws_iam_policy" "config_replication" {
  count = var.primary_region ? 1 : 0
  name        = local.config_replication_policy_name
  path        = "/"
  description = "IAM policy for figgy replication management lambdas"
  policy      = data.aws_iam_policy_document.config_replication_document[0].json

//  # Prevents TF from always detecting changes in the name even when there are none, causing resource recreation.
//  lifecycle {
//    ignore_changes = [name]
//  }
}

data "aws_iam_policy_document" "config_replication_document" {
  count = var.primary_region ? 1 : 0

  statement {
    sid = "ReplicationTableFullAccess"
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
    resources = ["arn:aws:dynamodb:*:${local.account_id}:table/${aws_dynamodb_table.config_replication.name}"]
  }

  statement {
    sid = "ReplicationTableStreamRead"
    actions = [
      "dynamodb:GetRecords",
      "dynamodb:GetShardIterator",
      "dynamodb:ListStreams",
      "dynamodb:ListShards",
      "dynamodb:DescribeStream"
    ]
    resources = [
      "arn:aws:dynamodb:*:${local.account_id}:table/${aws_dynamodb_table.config_replication.name}/stream/*",
    ]
  }

  statement {
    sid       = "KMSListKeys"
    actions   = ["kms:ListKeys"]
    resources = ["*"]
  }

  statement {
    sid = "FiggySSMAccess"
    actions = [
      "ssm:DeleteParameter",
      "ssm:DeleteParameters",
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:GetParameterHistory",
      "ssm:GetParametersByPath",
      "ssm:PutParameter",
      "ssm:AddTagsToResource"
    ]
    resources = distinct(concat(
      [
        for x in var.cfgs.root_namespaces :
        format("arn:aws:ssm:*:%s:parameter%s/*", data.aws_caller_identity.current.account_id, x)
      ],
      [
        for ns in var.cfgs.global_read_namespaces :
        "arn:aws:ssm:*:${data.aws_caller_identity.current.account_id}:parameter${ns}/*"
      ]
    ))
  }

  statement {
    sid       = "SSMDescribe"
    actions   = ["ssm:DescribeParameters"]
    resources = ["*"]
  }
}


# Read configs under /figgy namespace
resource "aws_iam_policy" "lambda_read_figgy_specific_configs" {
  count = var.primary_region ? 1 : 0
  name        = local.read_figgy_configs_policy_name
  path        = "/"
  description = "IAM policy to enable figgy lambdas to read figgy-specific configurations"
  policy      = data.aws_iam_policy_document.lambda_read_figgy_configs[0].json

//  # Prevents TF from always detecting changes in the name even when there are none, causing resource recreation.
//  lifecycle {
//    ignore_changes = [name]
//  }
}

data "aws_iam_policy_document" "lambda_read_figgy_configs" {
  count = var.primary_region ? 1 : 0

  statement {
    sid = "FiggySSMAccess"
    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:GetParameterHistory",
      "ssm:GetParametersByPath"
    ]
    resources = ["arn:aws:ssm:*:${data.aws_caller_identity.current.account_id}:parameter/figgy/*"]
  }

  statement {
    sid       = "SSMDescribe"
    actions   = ["ssm:DescribeParameters"]
    resources = ["*"]
  }
}

#Todo -- add back read for all configs -- cache syncer needs it.


# Read configs under user defined namespaces
resource "aws_iam_policy" "lambda_read_user_namespaced_configs" {
  count = var.primary_region ? 1 : 0
  name        = local.read_user_namespaced_configs
  path        = "/"
  description = "IAM policy to enable figgy lambdas to read figgy-managed namespaced configurations"
  policy      = data.aws_iam_policy_document.read_user_ns_configs[0].json

//  # Prevents TF from always detecting changes in the name even when there are none, causing resource recreation.
//  lifecycle {
//    ignore_changes = [name]
//  }
}


data "aws_iam_policy_document" "read_user_ns_configs" {
  count = var.primary_region ? 1 : 0

  statement {
    sid = "FiggyReadUserNamespacesOnly"
    actions = [
      "ssm:GetParameter",
      "ssm:GetParameters",
      "ssm:GetParameterHistory",
      "ssm:GetParametersByPath"
    ]

    resources = concat([
      for ns in var.cfgs.role_to_ns_access[var.cfgs.role_types[count.index]] :
      "arn:aws:ssm:*:${data.aws_caller_identity.current.account_id}:parameter${ns}/*"
      ], [
      for ns in var.cfgs.global_read_namespaces :
      "arn:aws:ssm:*:${data.aws_caller_identity.current.account_id}:parameter${ns}/*"
      ]
    )
  }

  statement {
    sid       = "SSMDescribe"
    actions   = ["ssm:DescribeParameters"]
    resources = ["*"]
  }
}