locals {
  # Cannot pass direct reference because these policy may be created by a different region's build
  cache_syncer_policies = [
    aws_iam_policy.config_cache_manager.arn,
    aws_iam_policy.lambda_default.arn,
    aws_iam_policy.lambda_read_figgy_specific_configs.arn
  ]
}

module "config_cache_syncer" {
  source         = "../figgy_lambda"
  deploy_bucket  = aws_s3_bucket.figgy_bucket.id
  description    = "Incrementally synchronizes the cache table used for auto-complete in the figgy CLI tool"
  handler        = "functions/config_cache_syncer.handle"
  lambda_name    = local.config_cache_syncer_name
  lambda_timeout = 500
  policies = local.cache_syncer_policies
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

module "config_cache_syncer_trigger" {
  source              = "../triggers/cron_trigger"
  lambda_name         = module.config_cache_syncer.name
  lambda_arn          = module.config_cache_syncer.arn
  schedule_expression = "rate(30 minutes)"

  providers = {
    aws = aws.region
  }
}
