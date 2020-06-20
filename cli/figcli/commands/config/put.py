import re

from figcli.config import *
from botocore.exceptions import ClientError
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

from figcli.commands.config.get import Get
from figcli.commands.config_context import ConfigContext
from figcli.commands.types.config import ConfigCommand
from figcli.data.dao.ssm import SsmDao
from figcli.input import Input
from figcli.svcs.observability.anonymous_usage_tracker import AnonymousUsageTracker
from figcli.svcs.observability.version_tracker import VersionTracker
from figcli.utils.utils import Utils
from figcli.views.rbac_limited_config import RBACLimitedConfigView


class Put(ConfigCommand):

    def __init__(self, ssm_init: SsmDao, colors_enabled: bool, config_context: ConfigContext,
                 config_view: RBACLimitedConfigView, get: Get):
        super().__init__(put, colors_enabled, config_context)
        self._ssm = ssm_init
        self._utils = Utils(colors_enabled)
        self._config_view = config_view
        self._get = get
        self._source_key = Utils.attr_if_exists(copy_from, config_context.args)

        self._select_name = [
            ('class:', 'Please input a PS Name: ')
        ]

        self._FILE_PREFIX = "file://"

    def _load_file(self, file_path: str) -> str:
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except FileNotFoundError:
            print(
                f"Provided file path: {file_path} is invalid. No file found.")
            exit(1)

    def put_param(self, key=None, loop=False, display_hints=True) -> None:
        """
        Allows a user to define a PS name and add a new parameter at that named location. User will be prompted for a
        value, desc, and whether or not the parameter is a secret. If (Y) is selected for the secret, will encrypt the
        value with the appropriately mapped KMS key with the user's role.

        :param key: If specified, the user will be prompted for the specified key. Otherwise the user will be prompted
                    to specify the PS key to set.
        :param loop: Whether or not to continually loop and continue prompting the user for more keys.
        :param display_hints: Whether or not to display "Hints" to the user. You may want to turn this off if you are
                              looping and constantly calling put_param with a specified key.
        """

        value, desc, notify, put_another = True, None, False, True

        if display_hints:
            print(f"{self.c.fg_bl}Hint:{self.c.rs} To upload a file's contents, pass in `file:///path/to/your/file` "
                  f"in the value prompt.")

        while put_another:
            try:

                if not key:
                    key = Input.input('Please input a PS Name: ', completer=self._config_view.get_config_completer())

                if self._source_key:
                    plain_key = '/'.join(key.strip('/').split('/')[2:])
                    source_key = f'{self._source_key}/{plain_key}'
                    orig_value, orig_description = self._get.get_val_and_desc(source_key)
                else:
                    orig_description = ''
                    orig_value = ''

                value = Input.input(f"Please input a value for {key}: ", default=orig_value if orig_value else '')

                if value.lower().startswith(self._FILE_PREFIX):
                    value = self._load_file(value.replace(self._FILE_PREFIX, ""))

                existing_desc = self._ssm.get_description(key)
                desc = Input.input(f"Please input an optional description: ", optional=True,
                              default=existing_desc if existing_desc else orig_description if orig_description else '')

                is_secret = Input.is_secret()
                parameter_type, kms_id = SSM_SECURE_STRING if is_secret else SSM_STRING, None
                if is_secret:
                    valid_keys = self._config_view.get_authorized_kms_keys()
                    if len(valid_keys) > 1:
                        key_name = Input.select_kms_key(valid_keys)
                    else:
                        key_name = valid_keys[0]

                    kms_id = self._config_view.get_authorized_key_id(key_name, self.run_env)

                notify = True

                self._ssm.set_parameter(key, value, desc, parameter_type, key_id=kms_id)
                if key not in self._config_view.get_config_completer().words:
                    self._config_view.get_config_completer().words.append(key)

            except ClientError as e:
                if "AccessDeniedException" == e.response['Error']['Code']:
                    print(f"\n\nYou do not have permissions to put a new config value at the path:"
                          f" {self.c.fg_bl}{key}{self.c.rs}")
                    print(f"Your role has access to the following namespaces: "
                          f"{self.c.fg_bl}{self._config_view.get_authorized_namespaces()}{self.c.rs}")
                    print(f"{self.c.fg_rd}Error message: {e.response['Error']['Message']}{self.c.rs}")
                else:
                    print(f"{self.c.fg_rd}Exception caught attempting to add config: {e}{self.c.rs}")

            print()
            if loop:
                to_continue = input(f"\nAdd another? (y/N): ")
                put_another = True if to_continue.lower() == 'y' else False
                key = None
            else:
                put_another = False

    @VersionTracker.notify_user
    @AnonymousUsageTracker.track_command_usage
    def execute(self):
        self.put_param(loop=True)
