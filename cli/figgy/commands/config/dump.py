from prompt_toolkit.shortcuts import prompt
from config import *
from data.dao.ssm import SsmDao
from data.dao.config import ConfigDao
from prompt_toolkit.completion import WordCompleter
from commands.types.config import ConfigCommand
from commands.config_context import ConfigContext
from config import *
from svcs.observability.usage_tracker import UsageTracker
from svcs.observability.version_tracker import VersionTracker
from utils.utils import *


class Dump(ConfigCommand):
    """
    Allows users to dump PS K/V hierarchy into JSON, straight to the terminal, or to a file itself.
    """

    def __init__(self, ssm_init: SsmDao, config_completer_init: WordCompleter, colors_enabled: bool,
                 context: ConfigContext):
        super().__init__(audit, colors_enabled, context)
        self._ssm = ssm_init
        self._config_completer = config_completer_init
        self._utils = Utils(colors_enabled)
        self._output_file = context.out_file
        self._prefix = context.prefix
        self.example = f"{self.c.fg_bl}{CLI_NAME} config {self.type} --env dev{self.c.rs} --prefix /app/demo-time " \
            f"--out /tmp/out_file.json"

    def _dump(self):
        usr_prefix = self._prefix  # type: str
        notify = False  # type: bool

        while not self._utils.is_valid_input(usr_prefix, 'Prefix', notify) \
                and not self._prefix:
            usr_prefix = prompt(f"Please input a Prefix to dump from: ", completer=self._config_completer)

        all_names = list(map(lambda x: x['Name'], self._ssm.get_all_parameters([usr_prefix])))  # type: List[str]
        all_vals = self._ssm.get_parameter_values(all_names, decrypt=False)  # type: List[Dict]
        json_output = {}
        for val in all_vals:
            json_output[val['Name']] = val['Value']

        if self._output_file:
            with open(self._output_file, "w") as file:
                json.dump(json_output, file, indent=4, sort_keys=True)
        else:
            print(json.dumps(json_output, indent=4, sort_keys=True))


    @VersionTracker.notify_user
    @UsageTracker.track_command_usage
    def execute(self):
        self._dump()
