# Provisions figgy_cloud from the module - beware if you mess with this!
module "figgy_cloud" {
  source = "./modules/figgy_cloud"
  aws_account_id = var.aws_account_id
  env_alias = var.env_alias
  cfgs = merge(local.cfgs, local.bastion_cfgs, local.other_cfgs)
  figgy_cw_log_retention = var.figgy_cw_log_retention
  max_session_duration = var.max_session_duration
  notify_deletes = var.notify_deletes
  webhook_url = var.webhook_url
  sandbox_deploy = var.sandbox_deploy
  regions = var.regions
  primary_region = true
}

############################################
### MULTI REGION DEPLOYMENT CONFIG BELOW ###
############################################

# Duplicate the below block for each extra region you want to deploy Figgy into.
# Be sure to update the providers {} block.

//
//module "figgy_cloud_us_west" {
//  source = "./modules/figgy_cloud"
//  aws_account_id = var.aws_account_id
//  env_alias = var.env_alias
//  cfgs = merge(local.cfgs, local.bastion_cfgs, local.other_cfgs)
//  figgy_cw_log_retention = var.figgy_cw_log_retention
//  max_session_duration = var.max_session_duration
//  notify_deletes = var.notify_deletes
//  webhook_url = var.webhook_url
//  sandbox_deploy = var.sandbox_deploy
//  regions = var.regions
//  primary_region = false
//  providers = {
//    aws = aws.us-west-1   # <--- update this as needed.
//  }
//}