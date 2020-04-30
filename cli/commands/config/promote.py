from botocore.exceptions import ClientError

from commands.config_context import ConfigContext
from commands.types.config import ConfigCommand
from data.dao.ssm import SsmDao
from utils.utils import *


class Promote(ConfigCommand):

    def __init__(self, source_ssm: SsmDao, dest_ssm: SsmDao, config_completer_init: WordCompleter,
                 colors_enabled: bool, config_context: ConfigContext):
        super().__init__(promote, colors_enabled, config_context)
        self._source_ssm = source_ssm
        self._dest_ssm = dest_ssm
        self._config_completer = config_completer_init
        self._utils = Utils(colors_enabled)

    def _promote(self):
        repeat = True
        parameters: List[Dict] = []
        while repeat:
            namespace = prompt(f"Please input a namespace prefix to promote: (i.e. /app/foo/): ",
                               completer=self._config_completer)
            if not self._utils.is_valid_input(namespace, "namespace", notify=False):
                continue

            self._utils.validate(re.match(r'^/app/.+$', namespace) is not None,
                                 "You must select an application namespace that begins with '/app/")

            try:
                parameters: List[Dict] = self._source_ssm.get_all_parameters([namespace])

                if not parameters and self._source_ssm.get_parameter(namespace):
                    parameters = [self._source_ssm.get_parameter_details(namespace)]

                if parameters:
                    repeat = False
                else:
                    print("No parameters found. Try again.\n")
            except ClientError as e:
                print(f"{Color.fg_rd}ERROR: >> {e}{self.c.rs}")
                continue

        for param in parameters:
            if 'KeyId' in param:
                print(f"Skipping param: {self.c.fg_bl}{param['Name']}{self.c.rs}. "
                      f"It is encrypted and cannot be migrated.\r\n")
            else:
                selection = prompt(f"Would you like to promote {param['Name']} (Y/n)? ",
                                   completer=WordCompleter(['Y', 'N'])).strip().lower()
                selection = selection if selection != '' else 'y'
                next_env = self._utils.get_next_env(self.run_env)
                if selection == 'y':
                    val = self._source_ssm.get_parameter(param['Name'])
                    description = param.get('Description', "")
                    self._dest_ssm.set_parameter(param['Name'], val, description, SSM_STRING)
                    print(f"Successfully promoted {self.c.fg_bl}{param['Name']}{self.c.rs} to {next_env}.\r\n")

    def _validate(self):
        self._utils.validate(self.run_env.env != prod, "You may not promote from within the prod environment. There"
                                                       " is no environment higher than prod.")

    def execute(self):
        self._validate()
        self._promote()
