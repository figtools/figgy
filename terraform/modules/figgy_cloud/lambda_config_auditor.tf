locals {
  # Cannot pass direct reference because these policy may be created by a different region's build
  auditor_policies = var.primary_region ? [
    aws_iam_policy.config_auditor[0].arn,
    aws_iam_policy.lambda_default[0].arn,
    aws_iam_policy.lambda_read_figgy_specific_configs[0].arn
  ] : [
    "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/${local.config_auditor_name}",
    "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/${local.lambda_default_policy_name}",
    "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/${local.read_figgy_configs_policy_name}",
  ]

}

module "config_auditor" {
  source         = "../figgy_lambda"
  deploy_bucket  = aws_s3_bucket.figgy_bucket.id
  description    = "Maintains the figgy audit database that is used for configuration restoration."
  handler        = "functions/config_auditor.handle"
  lambda_name    = local.config_auditor_name
  lambda_timeout = 60
  policies = local.auditor_policies
  zip_path                = data.archive_file.figgy.output_path
  layers                  = [var.cfgs.aws_sdk_layer_map[data.aws_region.current.name]]
  cw_lambda_log_retention = var.figgy_cw_log_retention
  sns_alarm_topic         = aws_sns_topic.figgy_alarms.arn
  sha256                  = data.archive_file.figgy.output_base64sha256
  memory_size             = 256
  concurrent_executions   = 5
}

module "config_auditor_trigger" {
  source           = "../triggers/cw_trigger"
  lambda_name      = module.config_auditor.name
  lambda_arn       = module.config_auditor.arn
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