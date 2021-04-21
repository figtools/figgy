# Default lambda policy
resource "aws_iam_policy" "lambda_default" {
  count = var.primary_region ? 1 : 0
  name        = local.lambda_default_policy_name
  path        = "/"
  description = "Default IAM policy for figgy lambda. Provides basic Lambda access, such as writing logs to CW."
  policy      = data.aws_iam_policy_document.cloudwatch_logs_write.json
}


# Config Auditor Lambda
resource "aws_iam_policy" "config_auditor" {
  count = var.primary_region ? 1 : 0
  name        = local.config_auditor_name
  path        = "/"
  description = "IAM policy for figgy config-auditor lambda"
  policy      = data.aws_iam_policy_document.config_auditor_document.json
}

data "aws_iam_policy_document" "config_auditor_document" {
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
    resources = [aws_dynamodb_table.config_auditor.arn]
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
  policy      = data.aws_iam_policy_document.config_usage_tracker.json
}

data "aws_iam_policy_document" "config_usage_tracker" {
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
      aws_dynamodb_table.config_usage_tracker.arn,
      aws_dynamodb_table.user_cache.arn
    ]
  }
}

# Config cache manager / syncer lambdas
resource "aws_iam_policy" "config_cache_manager" {
  count = var.primary_region ? 1 : 0
  name        = local.config_cache_manager_name
  path        = "/"
  description = "IAM policy for figgy config_cache_manager/syncer lambdas"
  policy      = data.aws_iam_policy_document.config_cache_manager_document.json
}

data "aws_iam_policy_document" "config_cache_manager_document" {
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
    resources = [aws_dynamodb_table.config_cache.arn]
  }

  statement {
    sid       = "SSMDescribe"
    actions   = ["ssm:DescribeParameters"]
    resources = ["*"]
  }
}

# Replication lambdas policy
resource "aws_iam_policy" "config_replication" {
  name        = local.config_replication_policy_name
  path        = "/"
  description = "IAM policy for figgy replication management lambdas"
  policy      = data.aws_iam_policy_document.config_replication_document.json
}

data "aws_iam_policy_document" "config_replication_document" {
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
    resources = [aws_dynamodb_table.config_replication.arn]
  }

  statement {
    sid = "ReplicationTableStreamRead"
    actions = [
      "dynamodb:GetRecords",
      "dynamodb:GetShardIterator",
      "dynamodb:ListStreams",
      "dynamodb:DescribeStream"
    ]
    resources = [aws_dynamodb_table.config_replication.stream_arn]
  }

  statement {
    sid = "FiggyKMSAccess"
    actions = [
      "kms:DescribeKey",
      "kms:Decrypt",
      "kms:Encrypt"
    ]

    resources = concat([for x in aws_kms_key.encryption_key : x.arn], [aws_kms_key.replication_key.arn])
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
  policy      = data.aws_iam_policy_document.lambda_read_figgy_configs.json
}

data "aws_iam_policy_document" "lambda_read_figgy_configs" {
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