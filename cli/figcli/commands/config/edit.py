import logging
import re

from figcli.config import *
from botocore.exceptions import ClientError
from npyscreen import Form, MultiLineEdit, NPSApp, BoxTitle
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

from figcli.commands.config_context import ConfigContext
from figcli.commands.types.config import ConfigCommand
from figcli.data.dao.ssm import SsmDao
from figcli.input import Input
from figcli.svcs.observability.anonymous_usage_tracker import AnonymousUsageTracker
from figcli.svcs.observability.version_tracker import VersionTracker
from figcli.utils.utils import Utils
from figcli.views.rbac_limited_config import RBACLimitedConfigView

log = logging.getLogger(__name__)


class MultiLineInput(BoxTitle):
    _contained_widget = MultiLineEdit


class EditApp(NPSApp):
    def __init__(self, name: str, value: str, description: str):
        self.name = name
        self.value = value if value else ''
        self.description = description if description else ''
        self.value_box = None
        self.description_box = None

    def main(self):
        edit_form = Form()
        self.value_box = edit_form.add(MultiLineInput, value=self.value, name=f'Input value for: {self.name}',
                                       max_height=12)
        self.description_box = edit_form.add(MultiLineInput, value=self.description, name="Optional Description: ",
                                             max_height=12)
        print(f"Value box: {self.value_box} - {self.description_box}")
        edit_form.edit()


class Edit(ConfigCommand):

    def __init__(self, ssm_init: SsmDao, colors_enabled: bool, config_context: ConfigContext,
                 config_view: RBACLimitedConfigView, config_completer: WordCompleter):
        super().__init__(edit, colors_enabled, config_context)
        self._ssm = ssm_init
        self._config_view = config_view
        self._utils = Utils(colors_enabled)
        self._config_completer = config_completer

    def edit(self) -> None:
        """
        Allows a user to define a PS name and add or edit a parameter at that location. Uses NPYscreen editor.
        """
        key = Input.input('Please input a PS Name: ', completer=self._config_completer)

        try:
            value, desc = self._ssm.get_parameter_with_description(key)
            edit_app = EditApp(key, value, desc)
            edit_app.run()

            value, desc = edit_app.value_box.value, edit_app.description_box.value
            log.info(f"Edited value: {value} - description: {desc}")

            is_secret = Input.is_secret()
            parameter_type, kms_id = SSM_SECURE_STRING if is_secret else SSM_STRING, None
            if is_secret:
                valid_keys = self._config_view.get_authorized_kms_keys()
                if len(valid_keys) > 1:
                    key_name = Input.select_kms_key(valid_keys)
                else:
                    key_name = valid_keys[0]

                kms_id = self._config_view.get_authorized_key_id(key_name, self.run_env)

            if not self._utils.is_valid_input(key, f"Parameter name", True) \
                    or not self._utils.is_valid_input(value, key, True):
                self._utils.error_exit("Invalid input detected, please resolve the issue and retry.")

            self._ssm.set_parameter(key, value, desc, parameter_type, key_id=kms_id)
            print(f"{self.c.fg_gr}{key} saved successfully.{self.c.rs}")
        except ClientError as e:
            if "AccessDeniedException" == e.response['Error']['Code']:
                denied = "AccessDeniedException" == e.response['Error']['Code']
                if denied and "AWSKMS; Status Code: 400;" in e.response['Error']['Message']:
                    print(f"\n{self.c.fg_rd}You do not have access to decrypt the value of: {key}{self.c.rs}")
                elif denied:
                    print(f"\n{self.c.fg_rd}You do not have access to Parameter: {key}{self.c.rs}")
                else:
                    raise
            else:
                self._utils.error_exit(f"{self.c.fg_rd}Exception caught attempting to add config: {e}{self.c.rs}")

    @VersionTracker.notify_user
    @AnonymousUsageTracker.track_command_usage
    def execute(self):
        self.edit()
