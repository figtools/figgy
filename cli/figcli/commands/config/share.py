from botocore.exceptions import ClientError
from prompt_toolkit import prompt

from figcli.commands.config_context import ConfigContext
from figcli.commands.types.config import ConfigCommand
from figcli.models.replication_config import ReplicationType, ReplicationConfig
from figcli.svcs.observability.anonymous_usage_tracker import AnonymousUsageTracker
from figcli.svcs.observability.version_tracker import VersionTracker
from figcli.utils.utils import *
from figcli.config.style.style import FIGGY_STYLE


class Share(ConfigCommand):

    def __init__(self, ssm_init, config_init, config_completer_init, colors_enabled: bool,
                 config_context: ConfigContext):
        super().__init__(share, colors_enabled, config_context)

        self._ssm = ssm_init
        self._config = config_init
        self._config_completer = config_completer_init
        self._utils = Utils(colors_enabled)

    def _share_param(self):
        """
        Enables sharing of parameters from one namespace to the /app/service-name/replicated namespace.
        Args:
            run_env: Run Environment
        """

        source_name_msg = [
            (f'class:{self.c.bl}', 'Input the PS Name you wish to share: ')
        ]

        dest_name_msg = [
            (f'class:{self.c.bl}', 'Input the destination of the shared value: ')
        ]

        share_another = True
        while share_another:
            print()
            key = prompt(source_name_msg, completer=self._config_completer, style=FIGGY_STYLE)
            if re.match(f"{self.context.defaults.service_ns}/.*", key):
                print(
                    f"{self.c.fg_rd}The SOURCE of replication may not be from within the "
                    f"{self.context.defaults.service_ns}/ namespace.{self.c.rs}\n")
                continue

            dest = prompt(dest_name_msg, completer=self._config_completer, style=FIGGY_STYLE)
            key_value = None
            try:
                key_value = self._ssm.get_parameter(key)
            except ClientError as e:
                denied = "AccessDeniedException" == e.response['Error']['Code']
                if denied and "AWSKMS; Status Code: 400;" in e.response['Error']['Message']:
                    print(f"{self.c.fg_rd}You do not have access to decrypt the value of Name: {key}{self.c.rs}")
                elif denied:
                    print(f"{self.c.fg_rd}You do not have access to Name: {key}{self.c.rs}")
                else:
                    raise

                self._utils.validate(key_value is not None,
                                     "Either the Name you provided to share does not exist or you do not have the "
                                     "proper permissions to share the provided Name.")

            namespace = self._utils.parse_namespace(dest)

            repl_config = ReplicationConfig(dest, self.run_env,
                                            namespace, key, ReplicationType(REPL_TYPE_APP))
            self._config.put_config_repl(repl_config)
            print(f"{self.c.fg_gr}{key} successfully shared{self.c.rs}")
            to_continue = input(f"Share another? (Y/n): ")
            to_continue = to_continue if to_continue != '' else 'y'
            share_another = to_continue.lower() == "y"

    @VersionTracker.notify_user
    @AnonymousUsageTracker.track_command_usage
    def execute(self):
        self._share_param()
