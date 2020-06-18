from botocore.exceptions import ClientError
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

from figcli.config.style.style import FIGGY_STYLE
from figcli.svcs.observability.anonymous_usage_tracker import AnonymousUsageTracker
from figcli.svcs.observability.version_tracker import VersionTracker
from figcli.utils.utils import *
from figcli.commands.types.config import ConfigCommand
from figcli.commands.config_context import ConfigContext
from figcli.data.dao.config import ConfigDao
from figcli.models.replication_config import ReplicationConfig
from figcli.data.dao.ssm import SsmDao


class Delete(ConfigCommand):

    def __init__(self, ssm_init: SsmDao, config_init: ConfigDao, context: ConfigContext, colors_enabled: bool,
                 config_completer: WordCompleter):
        super().__init__(delete, colors_enabled, context)
        self._ssm = ssm_init
        self._config = config_init
        self._utils = Utils(colors_enabled)
        self._config_completer = config_completer

        # Prompts for this file
        self._del_message = [
            ('class:', 'PS Name to Delete: ')
        ]

    def delete_param(self, key) -> bool:
        """
        Manages safe deletion through the CLI. Prevents deletion of replication sources. Prompts user for deletion of
        replication destinations.
        Args:
            key: PS Name / Key

        Returns: bool - T/F based on whether a parameter was actually deleted.
        """
        sources = self._config.get_cfgs_by_src(key, self.run_env)  # type: List[ReplicationConfig]
        repl_conf = self._config.get_config_repl(key, self.run_env)  # type: ReplicationConfig

        if len(sources) > 0:
            print(f"{self.c.fg_rd}You're attempting to delete a key that is the source for at least one "
                  f"replication config.{self.c.rs}\n{self.c.fg_bl}{key}{self.c.rs} is actively replicating to these"
                  f" destinations:\n")
            for src in sources:
                print(f"Dest: {self.c.fg_rd}{src.destination}{self.c.rs}. "
                      f"This config was created by {self.c.fg_bl}{src.user}{self.c.rs}. ")

            print(
                f"\r\n{self.c.fg_bl}{key}{self.c.rs} is a replication SOURCE. Deleting this source would effectively BREAK "
                f"replication to the above printed destinations. You may NOT delete sources that are actively "
                f"replicating. Please delete the above printed DESTINATIONS first. "
                f"Once they have been deleted, you will be allowed to delete this "
                f"SOURCE.")
            return False
        elif repl_conf is not None:
            selection = "unselected"
            while selection.lower() != "y" and selection.lower() != "n":
                repl_msg = [
                    (f'class:{self.c.rd}', f"{key} is an active replication destination created by "),
                    (f'class:{self.c.bl}', f"{repl_conf.user}. "),
                    (f'class:{self.c.rd}', f"Do you want to ALSO delete this replication config and "
                                           f"permanently delete {key}? "),
                    (f'class:', "(y/N): ")]
                selection = prompt(repl_msg, completer=WordCompleter(['Y', 'N']), style=FIGGY_STYLE)
                selection = selection if selection != '' else 'n'
                if selection.strip().lower() == "y":
                    self._config.delete_config(key, self.run_env)
                    self._ssm.delete_parameter(key)
                    print(f"{self.c.fg_gr}{key} and replication config destination deleted successfully.{self.c.rs}")
                    return True
                elif selection.strip().lower() == "n":
                    return False

        else:
            delete_msg = f"{self.c.fg_gr}{key} deleted successfully.{self.c.rs}\r\n"
            try:
                print(f"Trying delete {key}")
                self._ssm.delete_parameter(key)
            except ClientError as e:
                if e.response['Error']['Code'] == 'ParameterNotFound':
                    print(delete_msg)
                    return True
                elif "AccessDeniedException" == e.response['Error']['Code']:
                    print(f"{self.c.fg_rd}You do not have permissions to delete: {key}{self.c.rs}")
                    return False
                else:
                    raise

            print(delete_msg)
            return True

    def _delete_param(self):
        """
        Prompts user for a parameter name to delete, then deletes
        """
        # Add all keys
        key, notify, delete_another = None, False, True

        while not self._utils.is_valid_input(key, f"PS Name", notify) or delete_another:
            key = prompt(self._del_message, style=FIGGY_STYLE,
                         completer=self._config_completer)
            notify = True
            try:
                if self._utils.is_valid_input(key, 'PS Parameter', False):
                    if self.delete_param(key):
                        if key in self._config_completer.words:
                            self._config_completer.words.remove(key)
                else:
                    continue
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if "AccessDeniedException" == error_code:
                    print(f"\n\nYou do not have permissions to a new config value at the path: "
                          f"{self.c.fg_bl} {key} {self.c.rs}")
                    print(f"Developers may add keys under the following namespaces: "
                          f"{self.c.fg_bl} {self.c.rs}")
                    print(f"Error message: {e.response['Error']['Message']}")
                elif "ParameterNotFound" == error_code:
                    print(f"{self.c.fg_rd} The specified Name: {self.c.rs} {self.c.fg_bl} {key}{self.c.rs}"
                          f"{self.c.fg_rd} does not exist in the selected environment. Please try again.', red {self.c.rs}")
                else:
                    print(f"Exception caught attempting to delete config: {e.response['Message']}")

            print()
            to_continue = input(f"Delete another? (Y/n): ")
            to_continue = to_continue if to_continue != '' else 'y'
            delete_another = to_continue.lower() == "y"


    @VersionTracker.notify_user
    @AnonymousUsageTracker.track_command_usage
    def execute(self):
        self._delete_param()
