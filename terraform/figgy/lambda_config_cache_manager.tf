module "config_cache_manager" {
  source = "./modules/figgy_lambda"
  deploy_bucket = data.aws_s3_bucket.deploy_bucket.id
  description = "Manages a DDB cache of items that figgy uses to populate auto-complete locally."
  handler = "functions/config_cache_manager.handle"
  lambda_name = "figgy-config-cache-manager"
  lambda_timeout = 60
  policies = [aws_iam_policy.config_cache_manager.arn, aws_iam_policy.lambda_default.arn]
  zip_path = data.archive_file.figgy.output_path
}

module "config_cache_manager_trigger" {
  source = "./modules/triggers/cw_trigger"
  lambda_name = module.config_cache_manager.name
  lambda_arn = module.config_cache_manager.arn
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