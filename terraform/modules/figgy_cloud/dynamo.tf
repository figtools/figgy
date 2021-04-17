resource "aws_dynamodb_table" "config_replication" {
  name             = "figgy-config-replication"
  hash_key         = "destination"
  billing_mode     = "PAY_PER_REQUEST"
  stream_enabled   = "true"
  stream_view_type = "KEYS_ONLY"

  point_in_time_recovery {
    enabled = true
  }

  attribute {
    name = "destination"
    type = "S"
  }

  tags = {
    Name        = "figgy-config-replication"
    Environment = var.env_alias
    owner       = "devops"
    application = "figgy"
    created_by  = "figgy"
  }
}

resource "aws_dynamodb_table" "config_auditor" {
  name         = "figgy-config-auditor"
  hash_key     = "parameter_name"
  range_key    = "time"
  billing_mode = "PAY_PER_REQUEST"

  point_in_time_recovery {
    enabled = true
  }

  attribute {
    name = "parameter_name"
    type = "S"
  }

  attribute {
    name = "time"
    type = "N"
  }

  tags = {
    Name        = "figgy-config-auditor"
    Environment = var.env_alias
    owner       = "devops"
    application = "figgy"
    created_by  = "figgy"
  }
}

resource "aws_dynamodb_table" "config_cache" {
  name         = "figgy-config-cache"
  hash_key     = "parameter_name"
  range_key    = "last_updated"
  billing_mode = "PAY_PER_REQUEST"

  attribute {
    name = "parameter_name"
    type = "S"
  }

  attribute {
    name = "last_updated"
    type = "N"
  }

  tags = {
    Name        = "figgy-config-cache"
    Environment = var.env_alias
    owner       = "devops"
    application = "figgy"
    created_by  = "figgy"
  }
}


resource "aws_dynamodb_table" "user_tracker" {
  name         = "figgy-config-usage-tracker"
  hash_key     = "parameter_name"
  range_key    = "user"
  billing_mode = "PAY_PER_REQUEST"

  attribute {
    name = "parameter_name"
    type = "S"
  }

  attribute {
    name = "user"
    type = "S"
  }

  attribute {
    name = "last_updated"
    type = "N"
  }

  attribute {
    name = "empty_indexable_key"
    type = "S"
  }

  global_secondary_index {
    name               = "UserLastUpdatedIndex"
    hash_key           = "user"
    range_key          = "last_updated"
    projection_type    = "ALL"
  }

  global_secondary_index {
    name               = "LastUpdateOnlyIdx"
    hash_key           = "empty_indexable_key"
    range_key          = "last_updated"
    projection_type    = "INCLUDES"
    non_key_attributes = ["parameter_name"]
  }

  tags = {
    Name        = "figgy-config-usage-tracker"
    Environment = var.env_alias
    owner       = "devops"
    application = "figgy"
    created_by  = "figgy"
  }
}
