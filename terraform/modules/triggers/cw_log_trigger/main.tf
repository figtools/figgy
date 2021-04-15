
locals {
  is_get_param_event = "$.eventName = \"GetParameterHistory\" || $.eventName = \"GetParameter\" || $.eventName = \"GetParameters\" || $.eventName = \"GetParametersByPath\""
  is_api_call = "$.eventType = \"AwsApiCall\""
  is_ssm_event = "$.eventSource = \"ssm.amazonaws.com\" "
  log_group_split = split("/", var.log_group_name)
  log_group_friendly_name = local.log_group_split[length(local.log_group_split - 1)] // get last element of split.
}

resource "aws_cloudwatch_log_subscription_filter" "get_parameter_events_filter" {
  name            = "${var.lambda_name}-${local.log_group_friendly_name}-subscription"
  filter_pattern  = var.cw_filter_expression
  destination_arn = var.lambda_arn
  log_group_name = var.log_group_name
}
