# Figgy generates & stores parameters into ParameterStore under the `/figgy` namespace based on the user's
# selected configurations. These parameters help drive a custom configured figgy ecosystem & CLI based on user
# preferences
data "aws_caller_identity" "current" {}

# Need to store this parameter for some of our lambdas :) - this is not a secret!
resource "aws_ssm_parameter" "parameter_replication_key_id" {
  provider = aws.region
  name  = "/figgy/kms/replication-key-id"
  type  = "String"
  value = aws_kms_key.replication_key.key_id
  overwrite = true
}

# These are used by figgy CLI for looking up the appropriate KMS key for on-the-fly encryption
resource "aws_ssm_parameter" "encryption_key_id" {
  provider = aws.region
  count = length(var.cfgs.encryption_keys)
  name  = "/figgy/kms/${var.cfgs.encryption_keys[count.index]}-key-id"
  type  = "String"
  value = aws_kms_key.encryption_key[count.index].key_id
  overwrite = true
}

# These are used by figgy CLI to help the CLI only show the user parameters they have access to
resource "aws_ssm_parameter" "role_to_ns_access" {
  provider = aws.region
  count       = length(var.cfgs.role_types)
  name        = "/figgy/rbac/${var.cfgs.role_types[count.index]}/namespaces"
  type        = "String"
  value       = jsonencode(var.cfgs.role_to_ns_access[var.cfgs.role_types[count.index]])
  overwrite = true
  description = <<EOF
This does nothing to actually ENFORCE access, this parameter is only to improve the UX when using the figgy CLI so
users are not shown parameters they cannot administrate."
EOF
}

# These are used by figgy CLI to help the CLI only show the user parameters they have access to
resource "aws_ssm_parameter" "used_namespaces" {
  provider = aws.region
  name        = "/figgy/namespaces"
  type        = "String"
  value       = jsonencode(var.cfgs.root_namespaces)
  overwrite = true
  description = <<EOF
This does nothing to actually ENFORCE access, this parameter is only to improve the UX when using the figgy CLI so
users are not shown parameters they cannot administrate."
EOF
}

# These are used by figgy CLI to help the CLI only show the user parameters they have access to
resource "aws_ssm_parameter" "profile_kms_keys" {
  provider = aws.region
  name        = "/figgy/rbac/profile/keys"
  type        = "String"
  value       = jsonencode(var.cfgs.encryption_keys)
  overwrite = true
  description = <<EOF
A list of all KMS keys managed by figgy, except the replication key. Queried when users provide --profile option
EOF
}


# These are used by figgy CLI to help the CLI only show the user parameters they have access to
resource "aws_ssm_parameter" "service_namespace" {
  provider = aws.region
  name        = "/figgy/defaults/service-namespace"
  type        = "String"
  value       = var.cfgs.service_namespace
  overwrite = true
  description = <<EOF
Figgy will automatically run `sync` and `cleanup` commands against this namespace. This namespace is where
all application/service configurations should be stored.
EOF
}

# These are used by figgy CLI to help the CLI only show the user kms keys they have access to
resource "aws_ssm_parameter" "role_to_kms_access" {
  provider = aws.region
  count       = length(var.cfgs.role_types)
  name        = "/figgy/rbac/${var.cfgs.role_types[count.index]}/keys"
  type        = "String"
  value       = jsonencode(var.cfgs.role_to_kms_access[var.cfgs.role_types[count.index]])
  overwrite = true
  description = <<EOF
This does nothing to actually ENFORCE access, this parameter is only to improve the UX when using the figgy CLI so
users are not shown KMS keys do not have access to use"
EOF
}

# These are used by figgy CLI to help the CLI only show the user kms keys they have access to
resource "aws_ssm_parameter" "all_kms_keys" {
  provider = aws.region
  name        = "/figgy/kms/all-keys"
  type        = "String"
  value       = jsonencode(concat(var.cfgs.encryption_keys, [local.replication_key_alias_name]))
  overwrite = true
  description = <<EOF
This does nothing to actually ENFORCE access, this parameter is only to improve the UX when using the Figgy CLI or UI so
users are not shown KMS keys do not have access to use"
EOF
}

# These are used by figgy CLI for looking up appropriate user -> role mappings. These do not drive
# access, but are needed for the CLI user experience. Access is driven purely by IAM based RBAC.
resource "aws_ssm_parameter" "user_to_role_mappings" {
  provider = aws.region
  count = var.cfgs.bastion_enabled && var.cfgs.bastion_account_number == var.aws_account_id ? length(keys(var.cfgs.bastion_users)) : 0
  name  = "/figgy/users/${keys(var.cfgs.bastion_users)[count.index]}/roles"
  type  = "String"
  value = jsonencode(var.cfgs.bastion_users[keys(var.cfgs.bastion_users)[count.index]])
  overwrite = true
}

# These are used by the Figgy CLI to know what accounts exist and which ones a user can assume into
# for permission management.
resource "aws_ssm_parameter" "account_mappings" {
  provider = aws.region
  count = var.cfgs.bastion_enabled && var.cfgs.bastion_account_number == var.aws_account_id ? length(keys(var.cfgs.associated_accounts)) : 0
  name  = "/figgy/accounts/${keys(var.cfgs.associated_accounts)[count.index]}"
  type  = "String"
  value = var.cfgs.associated_accounts[keys(var.cfgs.associated_accounts)[count.index]]
  overwrite = true
}

resource "aws_ssm_parameter" "version" {
  provider = aws.region
  name        = "/figgy/cloud/version"
  type        = "String"
  value       = var.cfgs.version
  description = "Version associated with this deployment of Figgy Cloud"
  overwrite   = true
}

resource "aws_ssm_parameter" "account_id" {
  provider = aws.region
  name        = "/figgy/account_id"
  type        = "String"
  value       = data.aws_caller_identity.current.account_id
  description = "AWS AccountID associated with this account."
  overwrite   = true
}

resource "aws_ssm_parameter" "env_alias" {
  provider = aws.region
  name        = "/figgy/env_alias"
  type        = "String"
  value       = var.env_alias
  description = "This is the Figgy Run Environment associated with this account."
  overwrite   = true
}

resource "aws_ssm_parameter" "regions" {
  provider = aws.region
  name        = "/figgy/regions"
  type        = "String"
  value       = jsonencode(var.regions)
  description = "All regions figgy is deployed across for this environment."
  overwrite   = true
}

resource "aws_ssm_parameter" "region" {
  provider = aws.region
  name        = "/figgy/region"
  type        = "String"
  value       = local.region
  description = "Current active region."
  overwrite   = true
}

## Slack Configurations
resource "aws_ssm_parameter" "notify_deletes" {
  provider = aws.region
  name        = "/figgy/integrations/slack/notify-deletes"
  type        = "String"
  value       = var.cfgs.slack_webhook_url != "unconfigured" ? var.notify_deletes : "false"
  description = "Set this to 'false' for environments where you do not want to receive slack notifications on delete"
  overwrite   = true
}

resource "aws_ssm_parameter" "slack_webhook" {
  provider = aws.region
  count = var.cfgs.slack_webhook_url != "unconfigured" ? 1 : 0
  name  = "/figgy/integrations/slack/webhook-url"
  type  = "String"
  value = var.cfgs.slack_webhook_url
  overwrite = true
}

## Figgy one-time-secret kms key id
resource "aws_ssm_parameter" "ots_kms_key_id" {
  provider = aws.region
  count       = var.cfgs.utility_account_id == var.aws_account_id && var.primary_region ? 1 : 0
  name        = "/figgy/kms/${local.figgy_ots_key_alias_name}-key-id"
  type        = "String"
  value       = aws_kms_key.figgy_ots_key[count.index].key_id
  description = "The ARN of the figgy one-time-secret KMS key."
  overwrite   = true
}

resource "aws_ssm_parameter" "utility_account" {
  provider = aws.region
  name        = "/figgy/utility-account-id"
  type        = "String"
  value       = var.cfgs.utility_account_id
  description = "Account id for the designated figgy utility-account"
  overwrite   = true
}
