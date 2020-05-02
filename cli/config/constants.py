from pathlib import Path
from config.aws import *

VERSION = '0.0.1'
CLI_NAME = 'figgy'
CLI_LATEST_VERSION_PS_PATH = '/devops/devops-ci/figgy/latest-version'
WSS_TAIL_URL_PS_PATH = '/shared/devops/websockets/logtail/url'
WWS_AUTH_LAMBDA_ARN_PS_PATH = '/shared/devops/websockets/logtail/auth-lambda/arn'
#TODO: UPDATE THIS
CLI_BUCKET = 'figgy-bucket'
CLI_UPDATE_COMMAND = f'aws s3 cp s3://{CLI_BUCKET}/figgy/$$VERSION$$/$$OS$$/figgy$$SUFFIX$$ /your/install/path ' \
    f'--profile YOUR_CLI_PROFILE_NAME '

# Table-specific Constants
REPL_TABLE_NAME = "figgy-config-replication"
REPL_DEST_KEY_NAME = "destination"
REPL_RUN_ENV_KEY_NAME = "run_env"
REPL_SOURCE_ATTR_NAME = "source"
REPL_NAMESPACE_ATTR_NAME = "namespace"
REPL_TYPE_ATTR_NAME = "type"
REPL_TYPE_APP = "app"
REPL_TYPE_MERGE = "merge"
REPL_USER_ATTR_NAME = "user"

AUDIT_TABLE_NAME = "figgy-config-auditor"
AUDIT_PARAMETER_KEY_NAME = "parameter_name"
AUDIT_TIME_KEY_NAME = "time"
AUDIT_ACTION_ATTR_NAME = "action"
AUDIT_USER_ATTR_NAME = "user"

CACHE_TABLE_NAME = 'figgy-config-cache'
CACHE_PARAMETER_KEY_NAME = "parameter_name"
CACHE_LAST_UPDATED_KEY_NAME = "last_updated"
AUDIT_PARAMETER_ATTR_TYPE = "type"
AUDIT_PARAMETER_ATTR_VERSION = "version"
AUDIT_PARAMETER_ATTR_DESCRIPTION = "description"
AUDIT_PARAMETER_ATTR_VALUE = "value"
AUDIT_PARAMETER_ATTR_KEY_ID = "key_id"

# Plugin table constants
PLUGIN_TABLE_NAME = "plugin-state"
PLUGIN_SERVICE_KEY_NAME = "service_name"
PLUGIN_PLUGIN_KEY_NAME = "plugin_name"
PLUGIN_SHA_ATTR_NAME = "sha1"
PLUGIN_USER_ATTR_NAME = "user_name"

# Service State table Constants
SERVICE_STATE_TABLE_NAME = "service-state"
SERVICE_STATE_KEY_NAME = "service_name"
SERVICE_STATE_CVE_ATTR_NAME = "cve_overrides"

# Tfe Cache table constants
TFE_CACHE_TABLE_NAME = "tfe-cache"
TFE_RESOURCE_KEY_NAME = "resource_name"
TFE_TYPE_ATTR_NAME = "type"

# Service name cache table constants
SERVICE_NAME_CACHE_TABLE_NAME = "service-name-cache"
SERVICE_NAME_KEY_NAME = "service_name"

# Lambda Constants
CREDENTIALS_MGR_LAMBDA_NAME = 'py-tfe-credentials-manager'
LOGTAIL_AUTH_LAMBDA_NAME = 'logtail-ENV-generate_token'

# Legacy Decryption
LEGACY_KMS_ENCRYPTION_PREFIX = '53cur3D8'

# Merge Key constants
MERGE_KEY_PREFIX = "${"
MERGE_KEY_SUFFIX = "}"

# SSM Constants
SSM_SECURE_STRING = "SecureString"
SSM_STRING = "String"
SSM_PUT = 'PutParameter'
SSM_DELETE = 'DeleteParameter'

# Other PS Config constants
DEPLOY_GROUPS_PS_PREFIX = '/shared/deploy-groups/'

# ci-config.json json keys
REPLICATION_KEY = 'replication_config'
MERGE_KEY = 'merged_parameters'
CONFIG_KEY = 'app_parameters'
SHARED_KEY = 'shared_parameters'
REPOSITORY_KEY = "repositories"
IMPORTS_KEY = 'import'
OPTIONAL_NAMESPACE = 'namespace'
REPL_FROM_KEY = 'replicate_from'
SOURCE_NS_KEY = 'source_namespace'
PARAMETERS_KEY = 'parameters'
SERVICE_KEY = 'service'
PLUGIN_KEY = 'plugins'


# Replication Types:
repl_types = [REPL_TYPE_APP, REPL_TYPE_MERGE]


# Defaults file names
HOME = str(Path.home())
DECRYPTER_S3_PATH_PREFIX = f'figgy/decrypt/'
DEFAULTS_FILE_PATH = f'{HOME}/.figgy/devops/defaults'
AWS_CREDENTIALS_FILE_PATH = f'{HOME}/.aws/credentials'
AWS_CONFIG_FILE_PATH = f'{HOME}/.aws/config'
DECRYPTER_FILE_PATH = f'{HOME}/.figgy/devops/decrypt'
DECRYPTER_WIN_FILE_PATH = f'{HOME}/.figgy/devops/decrypt.exe'
CACHE_DIR = f'{HOME}/.figgy/devops/cache/sts'
CACHE_OTHER_DIR = f'{HOME}/.figgy/devops/cache/other'
DEFAULT_INSTALL_PATH = '/usr/local/bin/figgy'

# Defaults file keys
DEFAULTS_ROLE_KEY = 'role'
DEFAULT_ENV_KEY = 'default_env'
COLORS_ENABLED_KEY = 'colors'
OKTA_USER_KEY = 'user'

# Cache File keys
OKTA_SESSION_TOKEN_CACHE_KEY = 'session_token'
OKTA_SESSION_ID_CACHE_KEY = 'session_id'

# Plaform Constants
LINUX = "Linux"
MAC = "Darwin"
WINDOWS = "Windows"
ROOT_USER = "root"

# Build configs
OVERRIDE_KEYRING_ENV_VAR = "OVERRIDE_KEYRING"
ONE_WEEK_SECONDS = 60 * 60 * 24 * 7
