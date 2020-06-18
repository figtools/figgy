import time

from figcli.config import *
from datetime import datetime
from typing import List

from botocore.exceptions import ClientError
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from tabulate import tabulate

from figcli.commands.config.delete import Delete
from figcli.commands.config_context import ConfigContext
from figcli.commands.types.config import ConfigCommand
from figcli.data.dao.config import ConfigDao
from figcli.data.dao.ssm import SsmDao
from figcli.models.parameter_store_history import PSHistory
from figcli.models.restore_config import RestoreConfig
from figcli.svcs.kms import KmsSvc
from figcli.svcs.observability.anonymous_usage_tracker import AnonymousUsageTracker
from figcli.svcs.observability.version_tracker import VersionTracker
from figcli.utils.utils import Utils


class Restore(ConfigCommand):
    def __init__(
            self,
            ssm_init: SsmDao,
            kms_init: KmsSvc,
            config_init: ConfigDao,
            colors_enabled: bool,
            context: ConfigContext,
            config_completer: WordCompleter,
            delete: Delete
    ):
        super().__init__(restore, colors_enabled, context)
        self._config_context = context
        self._ssm = ssm_init
        self._kms = kms_init
        self._config = config_init
        self._utils = Utils(colors_enabled)
        self._point_in_time = context.point_in_time
        self._config_completer = config_completer
        self._delete = delete

    def _client_exception_msg(self, item: RestoreConfig, e: ClientError):
        if "AccessDeniedException" == e.response["Error"]["Code"]:
            print(
                f"\n\nYou do not have permissions to a new config value at the path: "
                f"{self.c.fg_bl}{item.ps_name}{self.c.rs}"
            )
        else:
            print(
                f"{self.c.fg_rd}Error message: "
                f"{e.response['Error']['Message']}{self.c.rs}"
            )

    def get_parameter_arn(self, parameter_name: str):
        account_id = self._ssm.get_parameter(ACCOUNT_ID_PATH)

        return f"arn:aws:ssm:us-east-1:{account_id}:parameter{parameter_name}"

    def _restore_param(self) -> None:
        """
        Allow the user to query a parameter store entry from dynamo, so we can query + restore it, if desired.
        """

        table_entries = []

        ps_name = prompt(f"Please input PS key to restore: ", completer=self._config_completer)

        print(f"Attempting to retrieve all restorable values of {ps_name}")
        items: List[RestoreConfig] = self._config.get_parameter_restore_details(ps_name)

        if len(items) == 0:
            print("No restorable values were found for this parameter.")
            return

        for i, item in enumerate(items):
            date = time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(item.ps_time / 1000)
            )

            # we need to decrypt the value, if encrypted, in order to show it to the user
            if item.ps_key_id:
                item.ps_value = self._kms.decrypt_with_context(
                    item.ps_value,
                    {"PARAMETER_ARN": self.get_parameter_arn(item.ps_name)},
                )
            table_entries.append([i, date, item.ps_value, item.ps_user])

        print(
            tabulate(
                table_entries,
                headers=["Item #", "Time Created", "Value", "User"],
                tablefmt="grid",
                numalign="center",
                stralign="left",
            )
        )

        choice = int(input("Which item number would you like to restore: "))

        item = items[choice] if items[choice] else None

        if not item:
            print(f"{item} wasn't a valid choice from the list. Aborting restore")
            return

        final_selection = input(
            f"Are you sure you want to restore item #{choice} and have it be the latest version? (y/N): "
        )
        if final_selection.lower() != "y":
            print("Okay, aborting restore")
            return

        key_id = None if item.ps_type == "String" else item.ps_key_id

        try:
            self._ssm.set_parameter(
                item.ps_name,
                item.ps_value,
                item.ps_description,
                item.ps_type,
                key_id=key_id,
            )

            current_value = self._ssm.get_parameter(item.ps_name)
            if current_value == item.ps_value:
                print("Restore was successful")
            else:
                print(
                    "Latest version in parameter store doesn't match what we restored."
                )
                print(
                    f"Current value: {current_value}.  Expected value: {item.ps_value}"
                )

        except ClientError as e:
            self._client_exception_msg(item, e)

    def _decrypt_if_applicable(self, entry: RestoreConfig) -> str:
        if entry.ps_type != "String":
            return self._kms.decrypt_with_context(
                entry.ps_value, {"PARAMETER_ARN": self.get_parameter_arn(entry.ps_name)}
            )
        else:
            return entry.ps_value

    def _restore_params_to_point_in_time(self):
        """
        Restores parameters as they were to a point-in-time as defined by the time provided by the users.
        Replays parameter history to that point-in-time so versioning remains intact.
        """

        ps_prefix = prompt(f"Which parameter store prefix would you like to recursively restore? "
                           f"(e.g., /app/demo-time): ", completer=self._config_completer)

        choice = input(f"Are you sure you want to recursively restore from prefix: {ps_prefix}? (y/N): ")
        if choice.lower() != "y":
            print("Aborting restore.")

        time_selected: str = ""

        try:
            time_selected = input("Seconds since epoch to restore latest values from: ")
            time_converted = datetime.fromtimestamp(float(time_selected))
        except ValueError as e:
            if "out of range" in e.args[0]:
                try:
                    time_converted = datetime.fromtimestamp(float(time_selected) / 1000)
                except ValueError as e:
                    print(
                        "Make sure you're using a format of either seconds or milliseconds since epoch."
                    )
                    return
            elif "could not convert" in e.args[0]:
                print(
                    f"The format of this input should be seconds since epoch. (e.g., 1547647091)\n"
                    f"Try using: https://www.epochconverter.com/ to convert your date to this specific format."
                )
                return
            else:
                print(
                    "An unexpected exception triggered: "
                    f"'{e}' while trying to convert {time_selected} to 'datetime' format."
                )
                return

        choice = input(
            f"Are you sure you want to restore latest values from date: {time_converted}? (y/N): "
        )
        if choice.lower() != "y":
            print("Aborting restore.")
            return

        ps_history: PSHistory = self._config.get_parameter_history_before_time(time_converted, ps_prefix)

        if len(ps_history.history.values()) == 0:
            print("No results found for time range.  Aborting.")
            return

        try:
            for item in ps_history.history.values():
                if item.cfg_at(time_converted).ps_action == SSM_PUT:

                    cfgs_before: List[RestoreConfig] = item.cfgs_before(time_converted)
                    cfg_at: RestoreConfig = item.cfg_at(time_converted)
                    ssm_value = self._ssm.get_parameter(item.name)
                    dynamo_value = self._decrypt_if_applicable(cfg_at)

                    if ssm_value != dynamo_value:
                        if ssm_value is not None:
                            self._ssm.delete_parameter(item.name)

                        for cfg in cfgs_before:
                            decrypted_value = self._decrypt_if_applicable(cfg)
                            print(f"Restoring: {cfg.ps_name} as value: {decrypted_value} with description: "
                                  f"{cfg.ps_description} and key: {cfg.ps_key_id if cfg.ps_key_id else 'Parameter was unencrypted'}")
                            print(f"Replaying version: {cfg.ps_version} of {cfg.ps_name}")

                            self._ssm.set_parameter(cfg.ps_name, decrypted_value, cfg.ps_description, cfg.ps_type,
                                                    cfg.ps_key_id)
                    else:
                        print(f"Value for cfg: {item.name} is current. Skipping.")
                else:
                    # This item must have been a delete, which means this config didn't exist at that time.
                    print(f"Checking if {item.name} exists. It was previously deleted.")
                    self._prompt_delete(item.name)
        except ClientError as e:
            self._utils.error_exit(f"Caught error when attempting restore. {e}")

    def _prompt_delete(self, name):
        param = self._ssm.get_parameter_encrypted(name)
        if param:
            selection = "unselected"
            while selection.lower() != "y" and selection.lower() != "n":
                selection = input(f"PS Name: {self.c.fg_bl}{name}{self.c.rs} did not exist at this restore time."
                                  f" Delete it? (y/N)")
                selection = selection if selection != '' else 'n'

            if selection.lower() == 'y':
                self._delete.delete_param(name)

    @VersionTracker.notify_user
    @AnonymousUsageTracker.track_command_usage
    def execute(self):
        if self._point_in_time:
            self._restore_params_to_point_in_time()
        else:
            self._restore_param()
