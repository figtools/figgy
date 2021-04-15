
resource "aws_cloudwatch_log_group" "figgy_trail_log_group" {
  name = "/figgy/cloudtrail/default-trail"
  # We do not want to retain cloudtrail logs for a long time.
  # We parse SSM related Get/List/Describe events immediately then discard.
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

resource "aws_iam_role_policy_attachment" "figgy_trail_to_cw_logs" {
  policy_arn = aws_iam_policy.figgy_write_cw_logs.arn
  role       = aws_iam_role.figgy_trail_to_cw_logs.name
}

# At this time it is not possible to filter out ONLY SSM events, but we _can_ disable management events and auto-clean
# up logs from S3 within 1 day so we're going with that! Once we can filter trails by data-events only and limit to SSM
# events we will update this.
resource "aws_cloudtrail" "figgy_cloudtrail" {
  count                         = var.cfgs.create_deploy_bucket == true && var.cfgs.configure_cloudtrail ? 1 : 0
  name                          = "figgy-trail"
  s3_bucket_name                = var.deploy_bucket
  include_global_service_events = false
  is_multi_region_trail         = false
  is_organization_trail         = false

  # CloudTrail requires the Log Stream wildcard
  cloud_watch_logs_group_arn = "${aws_cloudwatch_log_group.figgy_trail_log_group.arn}:*"
  cloud_watch_logs_role_arn  = aws_iam_role.figgy_trail_to_cw_logs.arn
  depends_on                 = [aws_s3_bucket_policy.cloudtrail_bucket_policy]
}
