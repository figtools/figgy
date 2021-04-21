module "config_usage_tracker" {
  source         = "../figgy_lambda"
  deploy_bucket  = local.bucket_name
  description    = "Tracks users who are fetching configurations from parameter store in figgy managed namespaces."
  handler        = "functions/config_usage_tracker.handle"
  lambda_name    = "figgy-config-usage-tracker"
  lambda_timeout = 60
  policies = [
    aws_iam_policy.config_usage_tracker.arn,
    aws_iam_policy.lambda_default.arn,
    aws_iam_policy.lambda_read_figgy_specific_configs.arn,
  ]
  zip_path                = data.archive_file.figgy.output_path
  layers                  = [var.cfgs.aws_sdk_layer_map[data.aws_region.current.name]]
  cw_lambda_log_retention = var.figgy_cw_log_retention
  sns_alarm_topic         = aws_sns_topic.figgy_alarms.arn
  sha256                  = data.archive_file.figgy.output_base64sha256
  memory_size             = 256
  concurrent_executions   = 5
}

# We do not want to consume all Cloudtrail events, instead we only want the ones relevant to ParameterStore. This CW
# filter will ensure we only process relevant events. In the future, once AWS allows us to only publish cloudtrail
# events to the log group that are SSM events, we can limit this filter.
locals {
  is_get_param_event = "$.eventName = \"GetParameterHistory\" || $.eventName = \"GetParameter\" || $.eventName = \"GetParameters\" || $.eventName = \"GetParametersByPath\""
  is_api_call        = "$.eventType = \"AwsApiCall\""
  is_ssm_event       = "$.eventSource = \"ssm.amazonaws.com\" "
}

module "config_usage_tracker_trigger" {
  source               = "../triggers/cw_log_trigger"
  lambda_name          = module.config_usage_tracker.name
  lambda_arn           = module.config_usage_tracker.arn
  log_group_name       = aws_cloudwatch_log_group.figgy_trail_log_group.name
  log_group_arn        = aws_cloudwatch_log_group.figgy_trail_log_group.arn
  cw_filter_expression = "{ ${local.is_api_call} && ${local.is_ssm_event} && ( ${local.is_get_param_event} ) }"
}

