module "config_usage_tracker" {
  source                  = "../figgy_lambda"
  deploy_bucket           = var.deploy_bucket
  description             = "Tracks users who are fetching configurations from parameter store in figgy managed namespaces."
  handler                 = "functions/config_usage_tracker.handle"
  lambda_name             = "figgy-config-usage-tracker"
  lambda_timeout          = 60
  policies                = [aws_iam_policy.config_usage_tracker.arn, aws_iam_policy.lambda_default.arn]
  zip_path                = data.archive_file.figgy.output_path
  layers                  = [var.cfgs.aws_sdk_layer_map[var.region]]
  cw_lambda_log_retention = var.figgy_cw_log_retention
  sns_alarm_topic         = aws_sns_topic.figgy_alarms.arn
  sha256                  = data.archive_file.figgy.output_base64sha256
  memory_size             = 256
  concurrent_executions   = 5
}

module "config_usage_tracker_trigger" {
  source           = "../triggers/cw_trigger"
  lambda_name      = module.config_usage_tracker.name
  lambda_arn       = module.config_usage_tracker.arn
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
      "GetParameter"
    ]
  }
}
PATTERN
}