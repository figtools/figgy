
resource "aws_cloudwatch_log_group" "figgy_trail_log_group" {
  provider = aws.region
  name = "/figgy/cloudtrail/default-trail"
  # We do not want to retain cloudtrail logs, we only need them long enough for our lambda
  # We parse SSM related Get/List/Describe events immediately then discard.
  # For exact details on cloudtrail event consumption, see modules/figgy_cloud/figgy_config_usage_tracker.tf
  retention_in_days = 1
}

resource "aws_iam_role" "figgy_trail_to_cw_logs" {
  provider = aws.region
  name = "${local.cloudtrail_role_name}-${local.region}"
  assume_role_policy = data.aws_iam_policy_document.figgy_trail_role_assume_policy.json

  lifecycle {
    ignore_changes = [name]
  }
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
  cloudtrail_role_name = "figgy-cloudtrail"
}

resource "aws_iam_role_policy_attachment" "figgy_trail_to_cw_logs" {
  provider = aws.region
  policy_arn = aws_iam_policy.figgy_write_cw_logs.arn
  role       = aws_iam_role.figgy_trail_to_cw_logs.name
}

# At this time it is not possible to limit our cloudtrail to only select SSM events, but we can auto-clean the cloudwatch log group
# and S3 bucket very quickly to ensure we are able to get what we need without burning too much space.
# Currently, the only pre-filter types for data resources are  S3 objects, Lambdas, or DynamoDb
# See https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/cloudtrail#data_resource
resource "aws_cloudtrail" "figgy_cloudtrail" {
  provider = aws.region
  name                          = "figgy-trail-${local.region}"
  s3_bucket_name                = aws_s3_bucket.figgy_bucket.id
  include_global_service_events = false
  is_multi_region_trail         = false
  is_organization_trail         = false

  depends_on                 = [
    aws_s3_bucket.figgy_bucket,
    aws_s3_bucket_policy.cloudtrail_bucket_policy,
    aws_cloudwatch_log_group.figgy_trail_log_group
  ]

  lifecycle {
    ignore_changes = [name]
  }
}
//
//# This trail will write to a CW Log group for deeper insights into Secret and Parameter utilization. Ths is required
//# For various functionality in Figgy UI / Figgy Pro -- This trail is separate so we can limit volume of logs
//# ingested into AWS Cloudwatch (which can become expensive)
//resource "aws_cloudtrail" "figgy_read_cloudtrail" {
//  provider = aws.region
//  name                          = "figgy-read-trail-${local.region}"
//  s3_bucket_name                = aws_s3_bucket.figgy_bucket.id
//  include_global_service_events = false
//  is_multi_region_trail         = false
//  is_organization_trail         = false
//
//  # CloudTrail requires the Log Stream wildcard
//  cloud_watch_logs_group_arn = "${aws_cloudwatch_log_group.figgy_trail_log_group.arn}:*"
//  cloud_watch_logs_role_arn  = aws_iam_role.figgy_trail_to_cw_logs.arn
//
//  event_selector {
//    read_write_type = "Read"
//    include_management_events = false
//  }
//
//  depends_on                 = [
//    aws_s3_bucket.figgy_bucket,
//    aws_s3_bucket_policy.cloudtrail_bucket_policy,
//    aws_cloudwatch_log_group.figgy_trail_log_group
//  ]
//
//  lifecycle {
//    ignore_changes = [name]
//  }
//}
