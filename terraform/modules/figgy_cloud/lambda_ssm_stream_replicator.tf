locals {
  # Cannot pass direct reference because these policy may be created by a different region's build
  stream_replicator_policies = [
    "arn:aws:iam::${local.account_id}:policy/${local.config_replication_policy_name}",
    "arn:aws:iam::${local.account_id}:policy/${local.lambda_default_policy_name}",
    "arn:aws:iam::${local.account_id}:policy/${local.read_figgy_configs_policy_name}",
  ]
}

module "ssm_stream_replicator" {
  source         = "../figgy_lambda"
  deploy_bucket  = aws_s3_bucket.figgy_bucket.id
  description    = "Listens to the CW event stream for SSM events and triggers replication if replication sources are changed."
  handler        = "functions/ssm_stream_replicator.handle"
  lambda_name    = local.ssm_stream_replicator_name
  lambda_timeout = 60
  policies = local.stream_replicator_policies
  zip_path                = data.archive_file.figgy.output_path
  layers                  = [var.cfgs.aws_sdk_layer_map[data.aws_region.current.name]]
  cw_lambda_log_retention = var.figgy_cw_log_retention
  sns_alarm_topic         = aws_sns_topic.figgy_alarms.arn
  sha256                  = data.archive_file.figgy.output_base64sha256
  memory_size             = 256
  concurrent_executions   = 5
  create_role = var.primary_region

  providers = {
    aws = aws.region
  }
}

module "ssm_stream_replicator_trigger" {
  source           = "../triggers/cw_trigger"
  lambda_name      = module.ssm_stream_replicator.name
  lambda_arn       = module.ssm_stream_replicator.arn

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