resource "aws_cloudwatch_event_rule" "event_rule" {
  name = "${var.lambda_name}-cw-event"
  description = "This CW Event Triggers the Lambda: ${var.lambda_name}"
  event_pattern = var.cw_event_pattern
}

resource "aws_cloudwatch_event_target" "event_target" {
  target_id  = var.lambda_name
  arn        = var.lambda_arn
  rule       = aws_cloudwatch_event_rule.event_rule.name
}

resource "aws_lambda_permission" "lamda_permissions" {
  statement_id  = "CWInvokeFunction"
  action        = "lambda:InvokeFunction"
  function_name = var.lambda_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.event_rule.arn
}

locals {
  is_get_param_event = "$.eventName = \"GetParameterHistory\" || $.eventName = \"GetParameter\" || $.eventName = \"GetParameters\" || $.eventName = \"GetParametersByPath\""
  is_api_call = "$.eventType = \"AwsApiCall\""
  is_ssm_event = "$.eventSource = \"ssm.amazonaws.com\" "
  log_group_split = split("/", var.log_group_name)
  log_group_friendly_name = local.log_group_split[length(local.log_group_split - 1] // get last element of split.
}

resource "aws_cloudwatch_log_subscription_filter" "get_parameter_events_filter" {
  name            = "${var.lambda_name}-${local.log_group_friendly_name}-subscription"
  filter_pattern  = var.cw_filter_expression
  destination_arn = var.lambda_arn
  log_group_name = var.log_group_name
}

