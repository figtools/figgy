variable "env_alias" {
  description = "Environment alias. Defaults are dev/qa/stage/prod/mgmt but can be anything you like."
}

variable "region" {
  description = "AWS region to apply these configurations to"
}

variable "aws_account_id" {
  description = "Account id to enable role assumption for"
}

variable "max_session_duration" {
  description = "Max session duration in seconds for this assumed role. Default: 12 hours"
}

variable "webhook_url" {
  description = "Slack Webhook URL for figgy submit notifications such as parameter shares / critical figgy errors."
}

variable "sandbox_deploy" {
  description = "Ignore this and keep this false. This is only used for the figgy sandbox environment to facilitate the figgy playground."
}

variable "figgy_cw_log_retention" {
  description = "Number of days to keep figgy CW logs around. Must be 1, 3, 5, 7, 14, 30, 60, 90, 120, 150, 180, 365, 400, 545, 731, 1827, 3653"
}

variable "notify_deletes" {
  description = "Set to 'true' if you want to receive slack notifications when parameters are deleted in this environment."
}

variable "cfgs" {
  description = "Local configurations from the caller."
}

variable "regions" {
  type = list(string)
  description = "All AWS regions figgy is deployed in across this account."
}