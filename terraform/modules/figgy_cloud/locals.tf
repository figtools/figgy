data aws_region "current" {}

locals {

  # The figgy sandbox allows role assumption by accountId and by RoleId. This is unique to the figgy sandbox.
  principals = var.sandbox_deploy ? var.cfgs.sandbox_principals : var.cfgs.bastion_principal
  region = data.aws_region.current.name
  account_id = data.aws_caller_identity.current.account_id
}

