variable "run_env" {
  description = "Defaults are dev/qa/stage/prod/mgmt but can be anything you like."
}

variable "region" {
  description = "AWS region to apply these configurations to"
}

variable "aws_account_id" {
  description = "Account id to enable role assumption for"
}

variable "deploy_bucket" {
  description = "Bucket where your figgy lambdas will be deployed and versioned."
}

variable "max_session_duration" {
  description = "Max session duration in seconds for this assumed role. Default: 12 hours"
  default     = "43200"
}