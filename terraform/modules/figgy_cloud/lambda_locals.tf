locals {
  config_auditor_name = "figgy-config-auditor"
  config_cache_manager_name = "figgy-config-cache-manager"
  config_cache_syncer_name = "figgy-config-cache-syncer"
  config_usage_tracker_name = "figgy-config-usage-tracker"
  dynamo_stream_replicator_name = "figgy-dynamo-stream-replicator"
  replication_syncer_name = "figgy-replication-syncer"
  ssm_stream_replicator_name = "figgy-ssm-stream-replicator"

  # POLICIES
  lambda_default_policy_name = "figgy-lambda-default"
  config_replication_policy_name = "config-replication"
  read_figgy_configs_policy_name = "figgy-lambda-read-figgy-specific-configs"
  kms_decrypt_policy_name = "figgy-kms-decrypt"
}