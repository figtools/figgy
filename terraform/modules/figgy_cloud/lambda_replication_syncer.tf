locals {
  # Cannot pass direct reference because these policy may be created by a different region's build
  replication_syncer_policies = [
    "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/${local.config_replication_policy_name}",
    "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/${local.lambda_default_policy_name}",
    "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/${local.read_figgy_configs_policy_name}",
  ]

  replication_syncer_depends_on = var.primary_region ? [
    aws_iam_policy.config_replication,
    aws_iam_policy.lambda_default,
    aws_iam_policy.lambda_read_figgy_specific_configs
  ]: []
}

module "replication_syncer" {
  source         = "../figgy_lambda"
  deploy_bucket  = local.lambda_bucket
  description    = "Incrementally synchronizes the replication across all parameters in case something gets out-of-wack"
  handler        = "functions/replication_syncer.handle"
  lambda_name    = local.replication_syncer_name
  lambda_timeout = 300
  policies = replication_syncer_policies
  zip_path                = data.archive_file.figgy.output_path
  layers                  = [var.cfgs.aws_sdk_layer_map[data.aws_region.current.name]]
  cw_lambda_log_retention = var.figgy_cw_log_retention
  sns_alarm_topic         = aws_sns_topic.figgy_alarms.arn
  sha256                  = data.archive_file.figgy.output_base64sha256
  memory_size             = 256
  depends_on = replication_syncer_depends_on
}

module "replication_syncer_trigger" {
  source              = "../triggers/cron_trigger"
  lambda_name         = module.replication_syncer.name
  lambda_arn          = module.replication_syncer.arn
  schedule_expression = "rate(30 minutes)"
}
