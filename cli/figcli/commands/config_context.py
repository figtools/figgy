from typing import Optional

from figcli.models.defaults.defaults import CLIDefaults
from figcli.models.run_env import RunEnv
from figcli.models.role import Role
from figcli.commands.command_context import CommandContext
from figcli.commands.figgy_context import FiggyContext
from figcli.utils.utils import Utils
from figcli.config import *


class ConfigContext(CommandContext):
    """
    All `config` resource commands require this context for general use. Config commands operate differently based on
    Role and RunEnv

    The context also contains optional parameter values passed in via the original invoked command vai the CLI
    """

    def __init__(self, run_env: RunEnv, role: Role, args, resource: frozenset, defaults: Optional[CLIDefaults]):
        super().__init__(run_env, resource, defaults=defaults)
        self.role = role  # type: Role
        self.args = args
        self.ci_config_path = Utils.attr_if_exists(config, args)
        self.from_path = Utils.attr_if_exists(from_path, args)
        self.out_file = Utils.attr_if_exists(out, args)
        self.prefix = Utils.attr_if_exists(prefix, args)
        self.service = Utils.attr_if_exists(service, args)

        # Flags like --prompt that are unset or set to true
        self.repl = Utils.is_set_true(replication_only, args)
        self.manual = Utils.is_set_true(manual, args)
        self.point_in_time = Utils.is_set_true(point_in_time, args)
        self.all_profiles = Utils.is_set_true(all_profiles, args)
        self.skip_upgrade = Utils.is_set_true(skip_upgrade, args)
        self.replication_only = Utils.is_set_true(replication_only, args)
        self.point_in_time = Utils.is_set_true(point_in_time, args)
