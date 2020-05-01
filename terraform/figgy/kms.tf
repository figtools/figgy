# The `tags` blocks with `created_by: figgy` are important because they are leveraged by conditional blocks in
# IAM policies provisioned by serverless framework. This way we can give figgy Lambdas access to lambdas required
# for figgy execution and nothing more.

## 1 Key Per User Type
resource "aws_kms_key" "encryption_key" {
  count = length(local.encryption_keys)
  description = "Key used for encryption / decryption of ${local.encryption_keys[count.index]} secrets"
  tags = {
    "created_by": "figgy"
  }
}

resource "aws_kms_alias" "encryption_key_alias" {
  count = length(local.encryption_keys)
  name          = "alias/${local.encryption_keys[count.index]}-key"
  target_key_id = aws_kms_key.encryption_key[count.index].key_id
}

# Need to store this parameter for some of our lambdas :) - this is not a secret!
resource "aws_ssm_parameter" "encryption_key_id" {
  count = length(local.encryption_keys)
  name  = "/shared/iam/${local.encryption_keys[count.index]}-key-id"
  type  = "String"
  value = aws_kms_key.encryption_key[count.index].key_id
}

## Replication encryption key - this is required by figgy for the configuration sharing features (essential)
resource "aws_kms_key" "replication_key" {
  description = "Key used for encryption / decryption of replicated secrets"
  tags = {
    "created_by": "figgy"
  }
}

resource "aws_kms_alias" "replication_key_alias" {
  name          = "alias/replication-key"
  target_key_id = aws_kms_key.replication_key.key_id
}