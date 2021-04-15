
variable "lambda_name" {
  description = "function_name as defined in the lambda that was created"
}

variable "lambda_arn" {
  description = "ARN of lambda to apply expression to"
}

variable "log_group_name" {
  description = "CW Log group to subscribe the associated lambda to."
}

variable "cw_filter_expression" {
  description = "Filter expression to subselect log records by."
}