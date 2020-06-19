from botocore.exceptions import ClientError
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

from figcli.commands.config_context import ConfigContext
from figcli.commands.types.config import ConfigCommand
from figcli.data.dao.ssm import SsmDao
from figcli.input import Input
from figcli.svcs.observability.anonymous_usage_tracker import AnonymousUsageTracker
from figcli.svcs.observability.version_tracker import VersionTracker
from figcli.svcs.auth.session_manager import SessionManager
from figcli.utils.utils import *


# Todo: FIX - Prompt user for next environment since we can no longer assume what the next environment is
class Promote(ConfigCommand):

    def __init__(self, source_ssm: SsmDao, config_completer_init: WordCompleter,
                 colors_enabled: bool, config_context: ConfigContext, session_mgr: SessionManager):
        super().__init__(promote, colors_enabled, config_context)
        self.config_context = config_context
        self._source_ssm = source_ssm
        self._session_mgr = session_mgr
        self._config_completer = config_completer_init
        self._utils = Utils(colors_enabled)


    def _promote(self):
        repeat = True
        parameters: List[Dict] = []
        while repeat:
            namespace = prompt(f"Please input a namespace prefix to promote:"
                               f" (i.e. {self.context.defaults.service_ns}/foo/): ",
                               completer=self._config_completer)
            if not self._utils.is_valid_input(namespace, "namespace", notify=False):
                continue

            try:
                parameters: List[Dict] = self._source_ssm.get_all_parameters([namespace])

                if not parameters and self._source_ssm.get_parameter(namespace):
                    parameters = [self._source_ssm.get_parameter_details(namespace)]

                if parameters:
                    repeat = False
                else:
                    print("No parameters found. Try again.\n")
            except ClientError as e:
                print(f"{self.c.fg_rd}ERROR: >> {e}{self.c.rs}")
                continue

        print(f'{self.c.fg_bl}Found {len(parameters)} parameters to migrate.{self.c.rs}\n')

        assumable_roles = self.context.defaults.assumable_roles
        matching_roles = list(set([x for x in assumable_roles if x.role == self.config_context.role]))
        valid_envs = set([x.run_env.env for x in matching_roles])
        valid_envs.remove(self.run_env.env)  # Remove current env, we can't promote from dev -> dev
        next_env = Input.select(f'Please select the destination environment.', valid_options=list(valid_envs))

        matching_role = [role for role in matching_roles if role.run_env == RunEnv(next_env)][0]
        dest_ssm = SsmDao(self._session_mgr.get_session(matching_role, prompt=False).client('ssm'))

        for param in parameters:
            if 'KeyId' in param:
                print(f"Skipping param: {self.c.fg_bl}{param['Name']}{self.c.rs}. "
                      f"It is encrypted and cannot be migrated.")
            else:
                promote_it = Input.y_n_input(f"Would you like to promote: {param['Name']}?",
                                             default_yes=True)

                if promote_it:
                    val = self._source_ssm.get_parameter(param['Name'])
                    description = param.get('Description', "")
                    dest_ssm.set_parameter(param['Name'], val, description, SSM_STRING)
                    print(f"Successfully promoted {self.c.fg_bl}{param['Name']}{self.c.rs} to {next_env}.\r\n")


    @VersionTracker.notify_user
    @AnonymousUsageTracker.track_command_usage
    def execute(self):
        self._promote()
