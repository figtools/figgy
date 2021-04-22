
data "aws_region" "default" {}

data "aws_region" "current" {
  provider = aws.region
}

locals {

  # The figgy sandbox allows role assumption by accountId and by RoleId. This is unique to the figgy sandbox.
  principals = var.sandbox_deploy ? var.cfgs.sandbox_principals : var.cfgs.bastion_principal
  region = data.aws_region.current.name
  account_id = var.aws_account_id
}

