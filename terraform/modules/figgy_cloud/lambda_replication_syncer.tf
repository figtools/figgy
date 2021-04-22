locals {
  # Cannot pass direct reference because these policy may be created by a different region's build
  replication_syncer_policies = [
    aws_iam_policy.config_replication.arn,
    aws_iam_policy.lambda_default.arn,
    aws_iam_policy.lambda_read_figgy_specific_configs.arn
  ]
}

module "replication_syncer" {
  source         = "../figgy_lambda"
  deploy_bucket  = aws_s3_bucket.figgy_bucket.id
  description    = "Incrementally synchronizes the replication across all parameters in case something gets out-of-wack"
  handler        = "functions/replication_syncer.handle"
  lambda_name    = local.replication_syncer_name
  lambda_timeout = 300
  policies = local.replication_syncer_policies
  zip_path                = data.archive_file.figgy.output_path
  layers                  = [var.cfgs.aws_sdk_layer_map[data.aws_region.current.name]]
  cw_lambda_log_retention = var.figgy_cw_log_retention
  sns_alarm_topic         = aws_sns_topic.figgy_alarms.arn
  sha256                  = data.archive_file.figgy.output_base64sha256
  memory_size             = 256

  providers = {
    aws = aws.region
  }
}

module "replication_syncer_trigger" {
  source              = "../triggers/cron_trigger"
  lambda_name         = module.replication_syncer.name
  lambda_arn          = module.replication_syncer.arn
  schedule_expression = "rate(30 minutes)"

  providers = {
    aws = aws.region
  }
}
