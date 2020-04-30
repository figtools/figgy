import boto3
import argparse
import logging
from config import *
from models.run_env import RunEnv
from models.role import Role
from utils.utils import Utils
from typing import Optional, Dict, Union

logger = logging.getLogger(__name__)


class FiggyContext:
    """
    Contains contextual data required for building commands based on CLI input.
    """

    def __init__(self, colors_enabled: bool, resource: frozenset, command: frozenset,
                 run_env: RunEnv, role: Role, args: argparse.Namespace):

        Utils.stc_validate(args.command is not None, "No command found. Proper format is "
                                                     "`figgy <resource> <command> --option(s)`")
        self.colors_enabled = colors_enabled
        self.command: frozenset = command
        self.resource: frozenset = resource
        self.args = args
        self.run_env: RunEnv = run_env
        self.selected_role: Role = role
        self.ci_config_path = Utils.attr_if_exists(config, args)
        self.from_path = Utils.attr_if_exists(from_path, args)
        self.locals = Utils.attr_if_exists(locals_path, args)
        self.out_file = Utils.attr_if_exists(out, args)
        self.query_prefix = Utils.attr_if_exists(prefix, args)
        self.service = Utils.attr_if_exists(service, args)

        # Flags like --prompt that are unset or set to true
        self.repl = Utils.is_set_true(replication_only, args)
        self.manual = Utils.is_set_true(manual, args)
        self.point_in_time = Utils.is_set_true(point_in_time, args)
        self.all_profiles = Utils.is_set_true(all_profiles, args)
        self.skip_upgrade = Utils.is_set_true(skip_upgrade, args)

        logger.info(self.__dict__)
