# The `tags` blocks with `created_by: figgy` are important because they are leveraged by conditional blocks in
# IAM policies provisioned by serverless framework. This way we can give figgy Lambdas access to lambdas required
# for figgy execution and nothing more.

## DevOps encryption key
resource "aws_kms_key" "devops_key" {
  description = "Key used for encryption / decryption of devops application secrets"
  tags = {
    "created_by": "figgy"
  }
}

resource "aws_kms_alias" "devops_key_alias" {
  name          = "alias/devops-app-key"
  target_key_id = aws_kms_key.devops_key.key_id
}

## Developer encryption key
resource "aws_kms_key" "app_key" {
  description = "Key used for encryption / decryption of application secrets"
  tags = {
    "created_by": "figgy"
  }
}

resource "aws_kms_alias" "app_key_alias" {
  name          = "alias/app-key"
  target_key_id = aws_kms_key.app_key.key_id
}

## Data encryption key
resource "aws_kms_key" "data_key" {
  description = "Key used for encryption / decryption of data application secrets"
  tags = {
    "created_by": "figgy"
  }
}

resource "aws_kms_alias" "data_key_alias" {
  name          = "alias/data-key"
  target_key_id = aws_kms_key.data_key.key_id
}

## SRE encryption key
resource "aws_kms_key" "sre_key" {
  description = "Key used for encryption / decryption of SRE secrets"
  tags = {
    "created_by": "figgy"
  }
}

resource "aws_kms_alias" "sre_key_alias" {
  name          = "alias/sre-key"
  target_key_id = aws_kms_key.sre_key.key_id
}

## DBA encryption key
resource "aws_kms_key" "dba_key" {
  description = "Key used for encryption / decryption of DBA secrets"
  tags = {
    "created_by": "figgy"
  }
}

resource "aws_kms_alias" "dba_key_alias" {
  name          = "alias/dba-key"
  target_key_id = aws_kms_key.dba_key.key_id
}

## Replication encryption key
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

# Need to store this parameter for some of our lambdas :) - this is not a secret!
resource "aws_ssm_parameter" "parameter_replication_key_id" {
  name  = "/shared/iam/replication-key-id"
  type  = "String"
  value = aws_kms_key.replication_key.key_id
}