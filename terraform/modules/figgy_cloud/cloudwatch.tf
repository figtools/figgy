# Optionally, you may choose to send ALL figgy events to another account, like a security account.
# In the case of the figgy sandbox, where this is used, we send all events through the bastion account.

# Off by default - ship matching ParameterStore cloudwatch events to another
# account for global tracking.
resource "aws_cloudwatch_event_rule" "push_ps_events" {
  count         = var.sandbox_deploy && var.cfgs.bastion_account_number != var.aws_account_id && var.primary_region ? 1 : 0
  name          = "push-ssm-events"
  description   = "This CW Event Pushes ParameterStore events to another account's event bus. This is off by default and totally optional."
  event_pattern = <<PATTERN
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

resource "aws_cloudwatch_event_target" "push_event" {
  count     = var.sandbox_deploy && var.cfgs.bastion_account_number != var.aws_account_id && var.primary_region ? 1 : 0
  rule      = aws_cloudwatch_event_rule.push_ps_events[0].name
  target_id = "push-ps-events"
  arn       = "arn:aws:events:${data.aws_region.current.name}:${var.cfgs.bastion_account_number}:event-bus/default"
}


resource "aws_sns_topic" "figgy_alarms" {
  provider = aws.region
  name = "figgy-alarms"
}