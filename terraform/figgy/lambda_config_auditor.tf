module "config_auditor" {
  source = "./modules/figgy_lambda"
  deploy_bucket = data.aws_s3_bucket.deploy_bucket.id
  description = "Maintains the figgy audit database that is used for configuration restoration."
  handler = "functions/config_auditor.handle"
  lambda_name = "figgy-config-auditor"
  lambda_timeout = 60
  policies = [aws_iam_policy.config_auditor.arn, aws_iam_policy.lambda_default.arn]
  zip_path = data.archive_file.figgy.output_path
}

module "config_auditor_trigger" {
  source = "./modules/triggers/cw_trigger"
  lambda_name = module.config_auditor.name
  lambda_arn = module.config_auditor.arn
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