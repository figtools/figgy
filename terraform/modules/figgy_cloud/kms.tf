# Constants
locals {
  replication_key_alias_name = "replication"
  figgy_default_key_alias_name = "figgy-default"
  alias_suffix               = "-key"
  replication_key_alias      = "alias/${local.replication_key_alias_name}${local.alias_suffix}"
  figgy_default_key_alias    = "alias/${local.figgy_default_key_alias_name}${local.alias_suffix}"
}

# The `tags` blocks with `created_by: figgy` are important because they are leveraged by conditional blocks in
# IAM policies provisioned by serverless framework. This way we can give figgy Lambdas access to lambdas required
# for figgy execution and nothing more.

## 1 Key Per User Type
resource "aws_kms_key" "encryption_key" {
  provider    = aws.region
  count       = length(var.cfgs.encryption_keys)
  description = "Key used for encryption / decryption of ${var.cfgs.encryption_keys[count.index]} secrets"
  tags = {
    "created_by" : "figgy"
  }
}

resource "aws_kms_alias" "encryption_key_alias" {
  provider      = aws.region
  count         = length(var.cfgs.encryption_keys)
  name          = "alias/${var.cfgs.encryption_keys[count.index]}${local.alias_suffix}"
  target_key_id = aws_kms_key.encryption_key[count.index].key_id
}

## Figgy encryption key(s)
resource "aws_kms_key" "figgy_default_key" {
  provider    = aws.region
  count       = length(var.cfgs.figgy_encryption_keys)
  description = "Key used for encryption / decryption of figgy-specific secrets. Also used by some figgy utilities."
  tags = {
    "created_by" : "figgy"
  }
}

resource "aws_kms_alias" "figgy_default_key" {
  provider      = aws.region
  name          = local.figgy_default_key_alias
  target_key_id = aws_kms_key.figgy_default_key.id
}

## Replication encryption key - this is required by figgy for the configuration sharing features (essential)
resource "aws_kms_key" "replication_key" {
  provider    = aws.region
  description = "Key used for encryption / decryption of replicated secrets"
  tags = {
    "created_by" : "figgy"
  }
}

resource "aws_kms_alias" "replication_key_alias" {
  provider      = aws.region
  name          = local.replication_key_alias
  target_key_id = aws_kms_key.replication_key.key_id
}
