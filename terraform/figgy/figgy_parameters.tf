# Need to store this parameter for some of our lambdas :) - this is not a secret!
resource "aws_ssm_parameter" "parameter_replication_key_id" {
  name  = "/figgy/kms/replication-key-id"
  type  = "String"
  value = aws_kms_key.replication_key.key_id
}

# These are used by figgy CLI for looking up the appropriate KMS key for on-the-fly encryption
resource "aws_ssm_parameter" "encryption_key_ids" {
  count = length(local.encryption_keys)
  name  = "/figgy/kms/${local.encryption_keys[count.index]}-key-id"
  type  = "String"
  value = aws_kms_key.encryption_key[count.index].key_id
}

# These are used by figgy CLI for looking up the appropriate KMS key for on-the-fly encryption
resource "aws_ssm_parameter" "role_to_ns_access" {
  count = length(local.role_types)
  name  = "/figgy/rbac/${local.role_types[count.index]}"
  type  = "String"
  value = jsonencode(local.role_to_ns_access[local.role_types[count.index]])
}