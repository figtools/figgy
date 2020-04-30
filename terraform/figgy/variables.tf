variable "run_env" {
  description = "Defaults are dev/qa/stage/prod/mgmt but can be anything you like."
}

variable "region" {
  description = "AWS region to apply these configurations to"
}

variable "aws_account_id" {
  description = "Account id to enable role assumption for"
}

variable "okta_domain" {
  description = "Your OKTA domain without the `.okta.com` suffix. For a domain like `figgy.okta.com`, input `figgy`."
}

variable "deploy_bucket" {
  description = "Bucket where your figgy lambdas will be deployed and versioned."
}

variable "parameter_namespaces" {
  description = "List of top-level namespaces for figgy to know about and help manage. Figgy will only have access to these namespaces."
  default = ["/app", "/data", "/devops", "/sre", "/dba", "/shared"]
}