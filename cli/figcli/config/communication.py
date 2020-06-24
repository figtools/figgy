from figcli.config.commands import *
from figcli.config.constants import *
from figcli.config.figgy import *
from figcli.utils.collection_utils import CollectionUtils

# User communication text
CLEANUP_REPLICA_ORPHANS = "Some orphaned replication mappings were discovered for your service. " \
                          "Once they are no longer necessary please clean them up using the `cleanup` command."
SHARED_NAME_RESOLUTION_MESSAGE = f"Your application is missing at least one ParameterStore name that it expects to " \
                                 f"exist as defined in either the {SHARED_KEY} block of your configuration, or as a " \
                                 f"dependency of a merge key. To resolve " \
                                 f"this, contact whoever is responsible for sharing these config value(s) with you " \
                                 f"and have them setup up config replication of the values into your apps namespace " \
                                 f"at the expected path."
RESOURCE_PARSER_DESC = "Provides utilities to help manage application configs and secrets across all environments. " \
                       f" For more details run `{CLI_NAME} [resource] --help"
COMMAND_PARSER_DESC = "Provides utilities to help manage application configs and secrets across all environments. " \
                      f"For more details on commands, run: `{CLI_NAME} [resource] [command] --help`"
CONFIG_REQ_TEXT = f"--config is a requirement argument."
CI_CONFIG_HELP_TEXT = f"Path to your project's figgy.json file."
UNUSED_CONFIG_DETECTED = f"%%red%%The following Names were found in PS but are not referenced in your configurations. \n" \
                         f"Use the %%rs%%%%blue%%`cleanup`%%rs%%%%red%% command to clean them up once all " \
                         f"deployed application versions no longer use these configurations: %%rs%%"

# Help Text
VERSION_HELP_TEXT = f'Prints current version, which is, in this case: {VERSION}'
UPGRADE_HELP_TEXT = f'If available for your operating system, walks the user through an automatic upgrade process.'
SKIP_UPGRADE_HELP_TEXT = f'Prevents the figgy for checking for a new version. Useful when running E2E tests locally.'
COMMAND_HELP_TEXT = f'Valid values are: {CollectionUtils.printable_set(config_commands)}'
RESOURCE_HELP_TEXT = f'Valid values are: {CollectionUtils.printable_set(resources)}'
CONFIG_HELP_TEXT = f"Managed configuration resources. Commands: [{CollectionUtils.printable_set(config_commands)}]"
PROMPT_HELP_TEXT = f"With --prompt set you will always be prompted for your AWS CLI Profile name and user type."
REPLICATION_ONLY_HELP_TEXT = f"Sync a declarative replication-config json file that _only_ contains the {REPLICATION_KEY} block."
MANUAL_HELP_TEXT = f"Migrate any K/V Hierarchy, or a single KV Pair from Consul into anywhere in ParameterStore " \
                   f"(that you have permissions)."
IAM_HELP_TEXT = f"Manage your temporary credentials. [{CollectionUtils.printable_set(iam_commands)}]"
ENV_HELP_TEXT = f"Valid values are:"
INFO_HELP_TEXT = f"Prints out more detailed information about the selected subcommand."
CONFIGURE_HELP_TEXT = f"(Optional) Setup default configurations to reduce redundant prompts."
EMPTY_ENV_HELP_TEXT = f"No --env parameter found. Using default: "
DELETE_HELP_TEXT = f"Manually delete parameters from Parameter Store"
LIST_HELP_TEXT = f"Lists all matching configuration Names based on a namespace prefix. e.g. /app/demo-time/"
PUT_HELP_TEXT = f"Store (or update) an arbitrary configuration in ParameterStore."
SHARE_HELP_TEXT = f"Share a parameter from a source to an arbitrary destination path in Parameter Store via config " \
                  f"replication."
CLEANUP_HELP_TEXT = 'Cleanup will compare your config desired state as defined in your figgy.json with the current ' \
                    'config state in AWS. You will be prompted on whether or not you wish to delete orphaned ' \
                    'configurations (configs that exist in AWS but not in your figgy.json file).'
MIGRATE_HELP_TEXT = f"Walks a user through migrating application configs from Consul into Parameter Store"
SYNC_HELP_TEXT = "Synchronizes your defined figgy.json configurations with those in Parameter Store. " \
                 "This ensures the proper configurations exist in the provided run environment for your application."
GET_HELP_TEXT = "Retrieve an arbitrary value from ParameterStore by Name."
BROWSE_HELP_TEXT = "Browse and look up or delete parameters through a tree structure."
AUDIT_HELP_TEXT = "Audit parameter store changes to parameters."
DUMP_HELP_TEXT = "Dump a series of PS Values by a queried prefix as JSON, or output to a file."
PREFIX_HELP_TEXT = "The prefix (e.g. /app/demo-time) to limit results to."
OUT_HELP_TEXT = "File to write the outputted data to. e.g.: --out /tmp/some-file.json"
EXPORT_HELP_TEXT = "Writes temporary STS AWS credentials to your ~/.aws/credentials file under the [default] profile."

PROMOTE_HELP_TEXT = "Promote a set of configurations under an arbitrary app namespace to a higher environment."
RESTORE_HELP_TEXT = "Restore a single parameter or all parameters within a time range"
DEBUG_HELP_TEXT = "Turn on debug mode for enhanced logging."
EDIT_HELP_TEXT = "Edit the value of an existing parameter store parameter, or create a new one"
COPY_FROM_HELP_TEXT = "Copy values from another Parameter Store namespace."
GENERATE_HELP_TEXT = "Generate a new figgy.json file from an existing figgy.json file. This is useful when you " \
                     "want to deploy a single service multiple times under different names with slightly differing " \
                     "configurations."
FROM_HELP_TEXT = "/path/to/figgy.json file to use as the source template file to generate from. Your generated file" \
                 " will automatically have all of the configurations from the source-file configured to replicate to it."
LOGIN_HELP_TEXT = "Logs you in to all viable AWS accounts and caches session locally. This will prevent you from " \
                  "having to input your MFA every time you swap into a new account or role. \n\nAlternate Use:" \
                  "`figgy login sandbox` will log you into the Figgy sandbox playground for hassle-free " \
                  "experimentation."
VALIDATE_HELP_TEXT = "Validates a `figgy.json` file and ensures all required configurations exist in ParameterStore. " \
                     "Exits with an error code if any defined configuration is missing."
LOGIN_SANDBOX_HELP_TEXT = "Get a temporary session from the free figgy sandbox and have fun, experiment, do whatever" \
                          "you want!"

MISSING_PS_NAME_MESSAGE = "Your application is missing at least one ParameterStore name that it expects to exist as " \
                          "defined in your figgy.json file. To resolve this issue, first try running your `figgy` " \
                          " `sync` command to validate and synchronize your expected configs."
PROFILE_HELP_TEXT = "Overrides all other figgy configurations and instead pulls ALL credentials from your local " \
                    "~/.aws/credentials file and uses that for all types of authorization. Ideal for CICD pipelines."

# Point in time (--point-in-time)
POINT_IN_TIME = "Restore all parameters to a point in time."

ALL_PROFILES = "Export all available AWS profiles to ~/.aws/credentials"
ROLE = "Specify role to run command with"

HELP_TEXT_MAP = {
    version: VERSION_HELP_TEXT,
    command: COMMAND_HELP_TEXT,
    resource: RESOURCE_HELP_TEXT,
    config: CONFIG_HELP_TEXT,
    prompt_com: PROMPT_HELP_TEXT,
    replication_only: REPLICATION_ONLY_HELP_TEXT,
    manual: MANUAL_HELP_TEXT,
    env: ENV_HELP_TEXT,
    info: INFO_HELP_TEXT,
    configure: CONFIGURE_HELP_TEXT,
    delete: DELETE_HELP_TEXT,
    list_com: LIST_HELP_TEXT,
    put: PUT_HELP_TEXT,
    share: SHARE_HELP_TEXT,
    cleanup: CLEANUP_HELP_TEXT,
    sync: SYNC_HELP_TEXT,
    get: GET_HELP_TEXT,
    browse: BROWSE_HELP_TEXT,
    audit: AUDIT_HELP_TEXT,
    dump: DUMP_HELP_TEXT,
    out: OUT_HELP_TEXT,
    prefix: PREFIX_HELP_TEXT,
    skip_upgrade: SKIP_UPGRADE_HELP_TEXT,
    restore: RESTORE_HELP_TEXT,
    point_in_time: POINT_IN_TIME,
    export: EXPORT_HELP_TEXT,
    iam: IAM_HELP_TEXT,
    promote: PROMOTE_HELP_TEXT,
    all_profiles: ALL_PROFILES,
    role: ROLE,
    debug: DEBUG_HELP_TEXT,
    edit: EDIT_HELP_TEXT,
    copy_from: COPY_FROM_HELP_TEXT,
    generate: GENERATE_HELP_TEXT,
    from_path: FROM_HELP_TEXT,
    login: LOGIN_HELP_TEXT,
    sandbox: LOGIN_SANDBOX_HELP_TEXT,
    validate: VALIDATE_HELP_TEXT,
    profile: PROFILE_HELP_TEXT,
    upgrade: UPGRADE_HELP_TEXT
}

# Other
SNS_EMAIL_SUBJECT = "Figgy error detected."
DESC_MISSING_TEXT = "None specified"

# Prompts:
is_secret = [
    ('class:', 'Is this value a secret? (y/N): ')
]

# Config defaults descriptions:
AUTO_MFA_DESC = "By enabling this option you will never be prompted for MFA. Instead figgy will save your " \
                "multi-factor secret in your OS keychain andwill generated one-time passcodes on your behalf. " \
                "You will need your MFA secret handy. **This is your MFA secret, NOT your six-digit code that " \
                "regularly generated."

OKTA_APP_LINK_DESC = "This is the 'Embed URL' linked to your OKTA SAML integration with AWS. For more details see " \
                     "the Figgy Docs OKTA setup guide."

OKTA_MFA_TYPE_DESC = "Your OKTA administrator selects specific MFA types that are supported for OKTA. " \
                     "For instance, GOOGLE = the Google Authenticator application. OKTA = Okta Verify - Push MFA."

