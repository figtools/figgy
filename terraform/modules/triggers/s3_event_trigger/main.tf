data "aws_caller_identity" "current" {}

resource "aws_s3_bucket_notification" "bucket_notification" {
  bucket = var.bucket_name

  lambda_function {
    lambda_function_arn = var.lambda_arn
    events              = [var.s3_event_types]
    filter_prefix       = var.filter_prefix
    filter_suffix       = var.filter_suffix
  }
}