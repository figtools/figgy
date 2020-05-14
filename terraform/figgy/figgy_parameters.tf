# Figgy generates & stores parameters into ParameterStore under the `/figgy` namespace based on the user's
# selected configurations. These parameters help drive a custom configured figgy ecosystem & CLI based on user
# preferences

# Need to store this parameter for some of our lambdas :) - this is not a secret!
resource "aws_ssm_parameter" "parameter_replication_key_id" {
  name  = "/figgy/kms/replication-key-id"
  type  = "String"
  value = aws_kms_key.replication_key.key_id
}

# These are used by figgy CLI for looking up the appropriate KMS key for on-the-fly encryption
resource "aws_ssm_parameter" "encryption_key_id" {
  count = length(local.encryption_keys)
  name  = "/figgy/kms/${local.encryption_keys[count.index]}-key-id"
  type  = "String"
  value = aws_kms_key.encryption_key[count.index].key_id
}

# These are used by figgy CLI to help the CLI only show the user parameters they have access to
resource "aws_ssm_parameter" "role_to_ns_access" {
  count = length(local.role_types)
  name  = "/figgy/rbac/${local.role_types[count.index]}"
  type  = "String"
  value = jsonencode(local.role_to_ns_access[local.role_types[count.index]])
  description =<<EOF
This does nothing to actually ENFORCE access, this parameter is only to improve the UX when using the figgy CLI so
users are not shown parameters they cannot administrate."
EOF
}

# These are used by figgy CLI for looking up appropriate user -> role mappings. These do not drive
# access, but are needed for the CLI user experience. Access is driven purely by IAM based RBAC.
resource "aws_ssm_parameter" "user_to_role_mappings" {
  count = local.enable_sso == false && local.bastion_account_number == var.aws_account_id ? length(keys(local.bastion_users)) : 0
  name  = "/figgy/users/${keys(local.bastion_users)[count.index]}/roles"
  type  = "String"
  value = jsonencode(local.bastion_users[keys(local.bastion_users)[count.index]])
}

# These are used by the Figgy CLI to know what accounts exist and which ones a user can assume into
# for permission management.
resource "aws_ssm_parameter" "account_mappings" {
  count = local.enable_sso == false && local.bastion_account_number == var.aws_account_id ? length(keys(local.associated_acounts)) : 0
  name  = "/figgy/accounts/${keys(local.associated_acounts)[count.index]}"
  type  = "String"
  value = local.associated_acounts[keys(local.associated_acounts)[count.index]]
}
