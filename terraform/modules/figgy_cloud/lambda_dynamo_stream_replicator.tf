
locals {
  # Cannot pass direct reference because these policy may be created by a different region's build
  dynamo_stream_replication_policies = var.primary_region ? [
    aws_iam_policy.config_replication[0].arn,
    aws_iam_policy.lambda_default[0].arn,
    aws_iam_policy.lambda_read_figgy_specific_configs[0].arn,
    aws_iam_policy.kms_decrypt.arn
  ] :  [
    "arn:aws:iam::${local.account_id}:policy/${local.config_replication_policy_name}",
    "arn:aws:iam::${local.account_id}:policy/${local.lambda_default_policy_name}",
    "arn:aws:iam::${local.account_id}:policy/${local.read_figgy_configs_policy_name}",
    aws_iam_policy.kms_decrypt.arn
  ]
}

module "dynamo_stream_replicator" {
  source         = "../figgy_lambda"
  deploy_bucket  = aws_s3_bucket.figgy_bucket.id
  description    = "Instantly replicates source -> destination configuration changes when someone uses figgy to alter replication mappings."
  handler        = "functions/dynamo_stream_replicator.handle"
  lambda_name    = local.dynamo_stream_replicator_name
  lambda_timeout = 300
  policies = local.dynamo_stream_replication_policies
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

module "dynamo_stream_replicator_trigger" {
  source            = "../triggers/ddb_trigger"
  lambda_name       = module.dynamo_stream_replicator.name
  dynamo_stream_arn = aws_dynamodb_table.config_replication.stream_arn
  depends_on = [module.dynamo_stream_replicator]

  providers = {
    aws = aws.region
  }
}
