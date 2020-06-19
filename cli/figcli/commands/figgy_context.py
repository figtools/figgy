import argparse
import logging
from figcli.config import *
from figcli.models.assumable_role import AssumableRole
from figcli.models.run_env import RunEnv
from figcli.models.role import Role
from figcli.utils.utils import Utils
from typing import Optional, Dict, Union, List, Set

logger = logging.getLogger(__name__)


class FiggyContext:
    """
    Contains contextual data required for building commands based on CLI input.
    """

    def __init__(self, colors_enabled: bool, resource: frozenset, command: frozenset,
                 run_env: RunEnv, role: AssumableRole, args: argparse.Namespace):
        self.colors_enabled = colors_enabled
        self.command: frozenset = command
        self.resource: frozenset = resource

        # This enables us to have "commands" without resources. Like `figgy login` instead of `figgy login login`.
        # Makes things a bit more flexible.
        self.command = self.command if command else resource

        self.args = args
        self.run_env: RunEnv = run_env
        self.selected_role: AssumableRole = role
        self.role: Role = self.selected_role.role if self.selected_role else None
        self.ci_config_path = Utils.attr_if_exists(config, args)
        self.from_path = Utils.attr_if_exists(from_path, args)
        self.out_file = Utils.attr_if_exists(out, args)
        self.query_prefix = Utils.attr_if_exists(prefix, args)
        self.service = Utils.attr_if_exists(service, args)
        self.profile = Utils.attr_if_exists(profile, args)

        # Flags like --prompt that are unset or set to true
        self.repl = Utils.is_set_true(replication_only, args)
        self.manual = Utils.is_set_true(manual, args)
        self.point_in_time = Utils.is_set_true(point_in_time, args)
        self.all_profiles = Utils.is_set_true(all_profiles, args)
        self.skip_upgrade = Utils.is_set_true(skip_upgrade, args)
        self.configure = Utils.is_set_true(configure, args)
        self.version = Utils.is_set_true(version, args)

        logger.info(self.__dict__)

    def has_optional_arguments(self, argument: frozenset):
        return Utils.is_set_true(argument, self.args)

    def find_matching_optional_arguments(self, arguments: List[frozenset]) -> Set[frozenset]:
        optional_args = set()
        for arg in arguments:
            if Utils.is_set_true(arg, self.args):
                optional_args.add(arg)

        return optional_args
