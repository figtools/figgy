output "arn" {
  value = aws_lambda_function.figgy_lambda.arn
}

output "name" {
  value = aws_lambda_function.figgy_lambda.function_name
}

output "cw_log_group_name" {
  value = aws_cloudwatch_log_group.lambda_log_group.name
}