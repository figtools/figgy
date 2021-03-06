
locals {
  # If primary region, attach X policies, if not, attach these other ones.
  cache_manager_policies = var.primary_region ? [
    aws_iam_policy.config_cache_manager[0].arn,
    aws_iam_policy.lambda_default[0].arn,
    aws_iam_policy.lambda_read_figgy_specific_configs[0].arn
  ] :  []
}

module "config_cache_manager" {
  source         = "../figgy_lambda"
  deploy_bucket  = aws_s3_bucket.figgy_bucket.id
  description    = "Manages a DDB cache of items that figgy uses to populate auto-complete for CLI users."
  handler        = "functions/config_cache_manager.handle"
  lambda_name    = local.config_cache_manager_name
  lambda_timeout = 60
  policies = local.cache_manager_policies
  zip_path                = data.archive_file.figgy.output_path
  layers                  = [var.cfgs.aws_sdk_layer_map[data.aws_region.current.name]]
  cw_lambda_log_retention = var.figgy_cw_log_retention
  sns_alarm_topic         = aws_sns_topic.figgy_alarms.arn
  sha256                  = data.archive_file.figgy.output_base64sha256
  memory_size             = 256
  concurrent_executions   = 1
  create_role = var.primary_region

  providers = {
    aws = aws.region
  }
}

module "config_cache_manager_trigger" {
  source           = "../triggers/cw_trigger"
  lambda_name      = module.config_cache_manager.name
  lambda_arn       = module.config_cache_manager.arn

  providers = {
    aws = aws.region
  }

  cw_event_pattern = <<PATTERN
{
  "source": [
    "aws.ssm"
  ],
  "detail-type": [
    "AWS API Call via CloudTrail"
  ],
  "detail": {
    "eventSource": [
      "ssm.amazonaws.com"
    ],
    "eventName": [
      "PutParameter",
      "DeleteParameter",
      "DeleteParameters"
    ]
  }
}
PATTERN
}