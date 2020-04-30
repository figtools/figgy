locals {
  deploy_path = "functions/${var.lambda_name}.zip"
}

resource "aws_lambda_function" "figgy_lambda" {
  s3_bucket        = var.deploy_bucket
  s3_key           = local.deploy_path
  function_name    = var.lambda_name
  handler          = var.handler
  role             = aws_iam_role.figgy_role.arn
  runtime          = "python3.7"
  description      = var.description
  depends_on       = [aws_iam_role.figgy_role]
  timeout          = var.lambda_timeout
  source_code_hash = filebase64sha256(var.zip_path)
  reserved_concurrent_executions = var.concurrent_executions
}

resource "aws_s3_bucket_object" "figgy_deploy" {
  bucket = var.deploy_bucket
  key    = local.deploy_path
  source = var.zip_path
  etag = filemd5(var.zip_path)
}