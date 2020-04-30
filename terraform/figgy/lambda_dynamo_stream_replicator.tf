module "dynamo_stream_replicator" {
  source = "./modules/figgy_lambda"
  deploy_bucket = data.aws_s3_bucket.deploy_bucket.id
  description = "Instantly replicates source -> destination configuration changes when someone uses figgy to alter replication mappings."
  handler = "functions/dynamo_stream_replicator.handle"
  lambda_name = "figgy-dynamo-stream-replicator"
  lambda_timeout = 300
  policies = [aws_iam_policy.config_replication.arn, aws_iam_policy.lambda_default.arn]
  zip_path = data.archive_file.figgy.output_path
}

module "dynamo_stream_replicator_trigger" {
  source = "./modules/triggers/ddb_trigger"
  lambda_name = module.dynamo_stream_replicator.name
  dynamo_stream_arn = aws_dynamodb_table.config_replication.stream_arn
}
