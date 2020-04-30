from pathlib import Path
from config.aws import *
from config.constants import *

# Root subcommand types
version = frozenset({'version'})
command = frozenset({'command'})
resource = frozenset({'resource'})
configure = frozenset({'configure'})

# Resource types
config = frozenset({'config'})
iam = frozenset({'iam'})

resources = config | iam

# Config Sub Command definitions
sync = frozenset({'sync'})
put = frozenset({'put'})
restore = frozenset({'restore'})
point_in_time = frozenset({'point-in-time'})
delete = frozenset({'delete'})
cleanup = frozenset({'cleanup'})
get = frozenset({'get'})
edit = frozenset({'edit'})
list_com = frozenset({'list'})
share = frozenset({'share'})
promote = frozenset({'promote'})
ci_path = frozenset({'config'})
info = frozenset({'info'})
migrate = frozenset({'migrate'})
browse = frozenset({'browse'})
prompt_com = frozenset({'prompt'})
audit = frozenset({'audit'})
dump = frozenset({'dump'})
replication_only = frozenset({'replication-only'})
manual = frozenset({'manual'})
env = frozenset({'env'})
prefix = frozenset({'prefix'})
out = frozenset({'out'})
skip_upgrade = frozenset({'skip-upgrade'})
service = frozenset({'service'})
debug = frozenset({'debug'})
copy_from = frozenset({'copy-from'})
generate = frozenset({'generate'})
from_path = frozenset({'from'})

# IAM sub commands
export = frozenset({'export'})
all_profiles = frozenset({'all-profiles'})
role = frozenset({'role'})

# argparse options
help = frozenset({'help'})
required = frozenset({'required'})
action = frozenset({'action'})
store_true = 'store_true'

# Maps CLI `--options` for each argument, and sets flags if necessary
arg_options = {
    config: {
        cleanup: {
            config: {action: None, required: False},
            info: {action: store_true, required: False},
            prompt_com: {action: store_true, required: False},
            env: {action: None, required: False},
            skip_upgrade: {action: store_true, required: False},
            debug: {action: store_true, required: False}
        },
        delete: {
            info: {action: store_true, required: False},
            prompt_com: {action: store_true, required: False},
            env: {action: None, required: False},
            skip_upgrade: {action: store_true, required: False},
            debug: {action: store_true, required: False}
        },
        get: {
            info: {action: store_true, required: False},
            prompt_com: {action: store_true, required: False},
            env: {action: None, required: False},
            role: {action: None, required: False},
            skip_upgrade: {action: store_true, required: False},
            debug: {action: store_true, required: False}
        },
        list_com: {
            info: {action: store_true, required: False},
            prompt_com: {action: store_true, required: False},
            env: {action: None, required: False},
            role: {action: None, required: False},
            skip_upgrade: {action: store_true, required: False},
            debug: {action: store_true, required: False}
        },
        put: {
            info: {action: store_true, required: False},
            prompt_com: {action: store_true, required: False},
            env: {action: None, required: False},
            role: {action: None, required: False},
            skip_upgrade: {action: store_true, required: False},
            debug: {action: store_true, required: False}
        },
        edit: {
            info: {action: store_true, required: False},
            prompt_com: {action: store_true, required: False},
            env: {action: None, required: False},
            role: {action: None, required: False},
            skip_upgrade: {action: store_true, required: False},
            debug: {action: store_true, required: False}
        },
        restore: {
            info: {action: store_true, required: False},
            prompt_com: {action: store_true, required: False},
            env: {action: None, required: False},
            role: {action: None, required: False},
            point_in_time: {action: store_true, required: False},
            skip_upgrade: {action: store_true, required: False},
            debug: {action: store_true, required: False}
        },
        share: {
            info: {action: store_true, required: False},
            prompt_com: {action: store_true, required: False},
            env: {action: None, required: False},
            role: {action: None, required: False},
            skip_upgrade: {action: store_true, required: False},
            debug: {action: store_true, required: False}
        },
        sync: {
            info: {action: store_true, required: False},
            prompt_com: {action: store_true, required: False},
            env: {action: None, required: False},
            role: {action: None, required: False},
            replication_only: {action: store_true, required: False},
            config: {action: None, required: False},
            skip_upgrade: {action: store_true, required: False},
            debug: {action: store_true, required: False},
            copy_from: {action: None, required: False}
        },
        migrate: {
            info: {action: store_true, required: False},
            prompt_com: {action: store_true, required: False},
            env: {action: None, required: False},
            role: {action: None, required: False},
            config: {action: None, required: False},
            manual: {action: store_true, required: False},
            skip_upgrade: {action: store_true, required: False},
            debug: {action: store_true, required: False}
        },
        browse: {
            info: {action: store_true, required: False},
            prompt_com: {action: store_true, required: False},
            env: {action: None, required: False},
            role: {action: None, required: False},
            skip_upgrade: {action: store_true, required: False},
            debug: {action: store_true, required: False},
            prefix: {action: None, required: False}
        },
        dump: {
            info: {action: store_true, required: False},
            prompt_com: {action: store_true, required: False},
            env: {action: None, required: False},
            role: {action: None, required: False},
            prefix: {action: None, required: False},
            out: {action: None, required: False},
            skip_upgrade: {action: store_true, required: False},
            debug: {action: store_true, required: False}
        },
        audit: {
            info: {action: store_true, required: False},
            env: {action: None, required: False},
            role: {action: None, required: False},
            skip_upgrade: {action: store_true, required: False},
            debug: {action: store_true, required: False}
        },
        promote: {
            info: {action: store_true, required: False},
            env: {action: None, required: False},
            role: {action: None, required: False},
            skip_upgrade: {action: store_true, required: False},
            debug: {action: store_true, required: False}
        },
        generate: {
            info: {action: store_true, required: False},
            env: {action: None, required: False},
            from_path: {action: None, required: False},
            role: {action: None, required: False},
            skip_upgrade: {action: store_true, required: False},
            debug: {action: store_true, required: False}
        },
    },
    iam: {
        export: {
            info: {action: store_true, required: False},
            env: {action: None, required: False},
            skip_upgrade: {action: store_true, required: False},
            all_profiles: {action: store_true, required: False},
            role: {action: None, required: False},
            debug: {action: store_true, required: False}
        },
    }
}

# Merge key suffixes
merge_uri_suffix = ":uri"
empty_uri_suffix = ''
merge_suffixes = [merge_uri_suffix, empty_uri_suffix]

# Supported commands by resource
config_commands = [sync, put, edit, delete, cleanup, get, share, generate,
                   list_com, migrate, browse, audit, dump, restore, promote]
iam_commands = [export]

# Used to build out parser, map of resource to sub-commands
resource_map = {
    config: config_commands,
    iam: iam_commands,
}

options = ci_path | info


# KMS Key Types / Mapping
kms_app = 'app'
kms_data = 'data'
kms_devops = 'devops'
kms_keys = [kms_app, kms_data, kms_devops]
kms_key_id_map = {kms_app: APP_KEY_ID,
                  kms_data: DATA_KEY_ID, kms_devops: DEVOPS_KEY_ID}
usr_to_kms_map = {usr_data: DATA_KEY_ID, usr_dev: APP_KEY_ID, usr_devops: DEVOPS_KEY_ID,
                  usr_data_scientist: DATA_KEY_ID}

# Validation Supported types
plugin = "plugin"
cve = "cve"

# Command to option requirement map
REQ_OPTION_MAP = {
    cleanup: [ci_path],
    delete: [],
    get: [],
    list_com: [],
    migrate: [ci_path],
    put: [],
    restore: [],
    share: [],
    sync: [ci_path],
    edit: [],
    generate: [ci_path]
}

# Permission mappings
shared_ns = '/shared'
app_ns = '/app'
data_ns = '/data'
devops_ns = '/devops'
DEV_PS_WRITE_NS = ['/shared', '/app']

