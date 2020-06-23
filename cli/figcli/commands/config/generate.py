from os import getcwd
from typing import Tuple

from prompt_toolkit import prompt

from figcli.commands.config_context import ConfigContext
from figcli.commands.types.config import ConfigCommand
from figcli.svcs.observability.anonymous_usage_tracker import AnonymousUsageTracker
from figcli.svcs.observability.version_tracker import VersionTracker
from figcli.utils.utils import *

log = logging.getLogger(__name__)


class Generate(ConfigCommand):

    def __init__(self, colors_enabled: bool, config_context: ConfigContext):
        super().__init__(generate, colors_enabled, config_context)
        self._from_path = config_context.ci_config_path if config_context.ci_config_path else Utils.find_figgy_json()
        self._utils = Utils(colors_enabled)
        self._errors_detected = False
        self.example = f"{self.c.fg_bl}{CLI_NAME} config {self.command_printable} " \
            f"--env dev --config /path/to/config{self.c.rs}"

    @staticmethod
    def _get_service_name_and_version(service_name: str) -> Tuple[str, int]:
        base_matcher = re.compile(r"^([A-Za-z0-9_-]+)([0-9]+)$")
        result = base_matcher.match(service_name)
        base_name = result.group(1) if result else service_name
        version = int(result.group(2)) if result else 1

        return base_name, version

    def _generate(self):
        from_config = self._utils.get_ci_config(self._from_path)
        service_name = self._utils.get_namespace(from_config).split('/')[2]
        current_ns = self._utils.get_namespace(from_config)

        base_name, version = self._get_service_name_and_version(service_name)
        base_name = base_name if not base_name.endswith('-') else base_name[:-1]
        new_service_name = f'{base_name}-{version + 1}'

        new_name = prompt(f'Please select a new service name, it CANNOT be: {service_name}:  ',
                          default=new_service_name)
        self._utils.validate(new_name != service_name, f"You must select a new service name that differs from the one"
        f"designated in your source figgy.json file. "
        f"(NOT {service_name})")
        new_ns = f'{self.context.defaults.service_ns}/{new_name}/'

        # Update all configs destinations to leverage new namespace. Easiest to search/replace across everything.
        output_string = json.dumps(from_config)
        output_string = output_string.replace(current_ns[:-1], new_ns[:-1])
        new_config = json.loads(output_string)

        # Remove existing configs that will be replicated
        new_config[CONFIG_KEY] = []

        # Configure replicate_from block
        new_config[REPL_FROM_KEY] = {
            SOURCE_NS_KEY: from_config.get(REPL_FROM_KEY, {}).get(SOURCE_NS_KEY, current_ns),
            PARAMETERS_KEY: from_config.get(REPL_FROM_KEY, {}).get(PARAMETERS_KEY, [])
        }

        for param in from_config.get(CONFIG_KEY, []):
            new_config[REPL_FROM_KEY][PARAMETERS_KEY].append(self._utils.get_parameter_only(param))

        formatted_config = self._utils.format_config(new_config)
        current_dir = getcwd()
        output_file = prompt(f'Write new config here?: ', default=f'{current_dir}/{new_name}-config.json')
        self._utils.is_valid_input(output_file, "output_file", True)

        with open(output_file, "w") as file:
            file.write(json.dumps(formatted_config, sort_keys=False, indent=4))

        print(f'{self.c.fg_gr}New config successfully generated at location: {output_file}{self.c.rs}')

    @VersionTracker.notify_user
    @AnonymousUsageTracker.track_command_usage
    def execute(self):
        self._generate()
