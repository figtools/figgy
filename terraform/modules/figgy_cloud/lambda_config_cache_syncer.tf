locals {
  # Cannot pass direct reference because these policy may be created by a different region's build
  cache_syncer_policies = var.primary_region ? [
    aws_iam_policy.config_cache_manager[0].arn,
    aws_iam_policy.lambda_default[0].arn,
    aws_iam_policy.read_figgy_configs[0].arn
  ] :  [
    "arn:aws:iam::${local.account_id}:policy/${local.config_cache_manager_name}",
    "arn:aws:iam::${local.account_id}:policy/${local.lambda_default_policy_name}",
    "arn:aws:iam::${local.account_id}:policy/${local.read_figgy_configs_policy_name}",
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
  create_role = var.primary_region
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
