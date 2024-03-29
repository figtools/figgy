# Constants

# Replication Table
REPL_TABLE_NAME = "figgy-config-replication"
REPL_DEST_KEY_NAME = "destination"
REPL_RUN_ENV_KEY_NAME = "env_alias"
REPL_SOURCE_ATTR_NAME = "source"
REPL_NAMESPACE_ATTR_NAME = "namespace"
REPL_TYPE_ATTR_NAME = "type"
REPL_TYPE_APP = 'app'
REPL_TYPE_MERGE = 'merge'
REPL_USER_ATTR_NAME = 'user'

# Config cache table
CONFIG_CACHE_TABLE_NAME = "figgy-config-cache"
CONFIG_CACHE_PARAM_NAME_KEY = "parameter_name"
CONFIG_CACHE_STATE_ATTR_NAME = "state"
CONFIG_CACHE_LAST_UPDATED_KEY = "last_updated"
CONFIG_CACHE_STATE_DELETED = 'DELETED'
CONFIG_CACHE_STATE_ACTIVE = 'ACTIVE'

# Audit table
AUDIT_TABLE_NAME = "figgy-config-auditor"
AUDIT_PARAM_NAME_KEY = "parameter_name"
AUDIT_TIME_KEY = "time"
AUDIT_EVENT_TYPE_ATTR = "action"
AUDIT_USER_ATTR = "user"
AUDIT_VALUE_ATTR = "value"
AUDIT_TYPE_ATTR = "type"
AUDIT_KEYID_ATTR = "key_id"
AUDIT_DESCRIPTION_ATTR = "description"
AUDIT_VERSION_ATTR = "version"

# Config Usage Tracker
CONFIG_USAGE_TABLE_NAME = "figgy-config-usage-tracker"
CONFIG_USAGE_PARAMETER_KEY = "parameter_name"
CONFIG_USAGE_LAST_UPDATED_KEY = "last_updated"
CONFIG_USAGE_USER_KEY = "user"
CONFIG_USAGE_EMPTY_KEY = "empty_indexable_key"
CONFIG_USAGE_EMPTY_IDX_VALUE = "empty"

# User cache table
USER_CACHE_TABLE_NAME = "figgy-user-cache"
USER_CACHE_PARAM_NAME_KEY = "user_name"
USER_CACHE_STATE_ATTR_NAME = "state"
USER_CACHE_LAST_UPDATED_KEY = "last_updated"
USER_CACHE_STATE_DELETED = 'DELETED'
USER_CACHE_STATE_ACTIVE = 'ACTIVE'


# Generic
PUT_PARAM_ACTION = "PutParameter"
DELETE_PARAM_ACTION = "DeleteParameter"
DELETE_PARAMS_ACTION = "DeleteParameters"

SSM_SECURE_STRING = "SecureString"
REPL_KEY_PS_PATH = "/figgy/kms/replication-key-id"
ACCOUNT_ID_PS_PATH = "/figgy/account_id"
ACCOUNT_ENV_PS_PATH = "/figgy/env_alias"
NOTIFY_DELETES_PS_PATH = "/figgy/integrations/slack/notify-deletes"
FIGGY_WEBHOOK_URL_PATH = "/figgy/integrations/slack/webhook-url"
FIGGY_NAMESPACES_PATH = "/figgy/namespaces"

FIGGY_OTS_NAMESPACE = "/figgy/ots"
FIGGY_NAMESPACE = "/figgy"

# For PS items stored with this value, we will auto-clean them up. Used for automated E2E testing.
DELETE_ME_VALUE = 'DELETE_ME'
CIRCLECI_USER_NAME = 'circleci'
TEST_VALUE_KEEP_TIME = 10
