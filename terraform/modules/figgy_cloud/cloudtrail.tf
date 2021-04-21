
resource "aws_cloudwatch_log_group" "figgy_trail_log_group" {
  name = "/figgy/cloudtrail/default-trail"
  # We do not want to retain cloudtrail logs, we only need them long enough for our lambda
  # We parse SSM related Get/List/Describe events immediately then discard.
  # For exact details on cloudtrail event consumption, see modules/figgy_cloud/figgy_config_usage_tracker.tf
  retention_in_days = 1
}

resource "aws_iam_role" "figgy_trail_to_cw_logs" {
  assume_role_policy = data.aws_iam_policy_document.figgy_trail_role_assume_policy.json
}

data "aws_iam_policy_document" "figgy_trail_role_assume_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["cloudtrail.amazonaws.com"]
    }
  }
}

locals {
  write_cw_logs_policy_arn = var.primary_region ?
    aws_iam_policy.figgy_write_cw_logs.arn :
    "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/${local.config_auditor_name}",
}

resource "aws_iam_role_policy_attachment" "figgy_trail_to_cw_logs" {
  policy_arn = local.write_cw_logs_policy_arn
  role       = aws_iam_role.figgy_trail_to_cw_logs.name
}

# At this time it is not possible to limit our cloudtrail to only select SSM events, but we can auto-clean the cloudwatch log group
# and S3 bucket very quickly to ensure we are able to get what we need without burning too much space.
# Currently, the only pre-filter types for data resources are  S3 objects, Lambdas, or DynamoDb
# See https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudtrail#data_resource
resource "aws_cloudtrail" "figgy_cloudtrail" {
  name                          = "figgy-trail"
  s3_bucket_name                = local.bucket_name
  include_global_service_events = false
  is_multi_region_trail         = false
  is_organization_trail         = false

  # CloudTrail requires the Log Stream wildcard
  cloud_watch_logs_group_arn = "${aws_cloudwatch_log_group.figgy_trail_log_group.arn}:*"
  cloud_watch_logs_role_arn  = aws_iam_role.figgy_trail_to_cw_logs.arn
  depends_on                 = [
    aws_s3_bucket.figgy_bucket,
    aws_s3_bucket_policy.cloudtrail_bucket_policy,
    aws_cloudwatch_log_group.figgy_trail_log_group
  ]
}
