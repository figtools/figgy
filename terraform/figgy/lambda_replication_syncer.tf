module "replication_syncer" {
  source = "./modules/figgy_lambda"
  deploy_bucket = data.aws_s3_bucket.deploy_bucket.id
  description = "Incrementally synchronizes the replication across all parameters in case something gets out-of-wack"
  handler = "functions/replication_syncer.handle"
  lambda_name = "figgy-replication-syncer"
  lambda_timeout = 300
  policies = [aws_iam_policy.config_replication.arn, aws_iam_policy.lambda_default.arn]
  zip_path = data.archive_file.figgy.output_path
}

module "replication_syncer_trigger" {
  source = "./modules/triggers/cron_trigger"
  lambda_name = module.replication_syncer.name
  lambda_arn = module.replication_syncer.arn
  schedule_expression = "rate(30 minutes)"
}
