import boto3
import botocore
import time
import logging

from prompt_toolkit.completion import WordCompleter


from commands.config_context import ConfigContext
from commands.config_factory import ConfigFactory
from commands.iam_context import IAMContext
from commands.iam_factory import IAMFactory
from commands.factory import Factory
from models.defaults import CLIDefaults
from models.run_env import RunEnv
from models.role import Role
from commands.figgy_context import FiggyContext
from svcs.kms import KmsSvc
from svcs.config import ConfigService
from svcs.cache_manager import CacheManager
from svcs.session_manager import SessionManager
from data.dao.config import ConfigDao
from utils.utils import Utils
from config import *
from data.dao.ssm import SsmDao
from typing import Optional, List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor, thread, as_completed

logger = logging.getLogger(__name__)


class CommandFactory(Factory):
    """
    Uses the provided FiggyContext (which contains details of args passed in, etc), and initializes a command
    factory of the appropriate type, and generates the appropriate command.
    """

    def __init__(self, context: FiggyContext, cli_defaults: CLIDefaults):
        self._context = context
        self._utils = Utils(context.colors_enabled)
        self._cli_defaults = cli_defaults
        self._session_manager = SessionManager(self._context.colors_enabled, self._cli_defaults)

        self._env_session = None
        self._mgmt_session = None
        self._next_env = None
        self._ssm = None
        self._config = None
        self._kms = None
        self._mgmt_s3_rsc = None
        self._all_sessions = None
        self._config_completer = None
        self._config_svc = None
        self._cache_mgr = None

    def __env_session(self) -> boto3.session.Session:
        """
        Lazy load an ENV session object for the ENV selected in the FiggyContext
        :return: Hydrated session for the selected environment.
        """
        if not self._env_session:
            self._env_session = self._session_manager.get_session(
                self._context.run_env,
                self._context.selected_role,
                prompt=False)

        return self._env_session

    def __mgmt_session(self) -> boto3.session.Session:
        """
        Lazy load an MGMT session object for the MGMT environment
        :return: Hydrated session for the mgmt environment.
        """
        if not self._mgmt_session:
            self._mgmt_session = self._session_manager.get_session(
                RunEnv(mgmt),
                self._context.selected_role,
                prompt=False)

        return self._mgmt_session

    def __next_env(self) -> boto3.session.Session:
        """
        Lazy load an ENV session object for the ENV AFTER the selected ENV in the FiggyContext
        :return: Hydrated session for the selected + 1 environment.
        """
        if not self._next_env:
            next_env = Utils.get_next_env(self._context.run_env)
            self._next_env: boto3.Session = self._session_manager.get_session(
                next_env,
                self._context.selected_role,
                prompt=False)

        return self._next_env

    def __next_ssm(self) -> SsmDao:
        """
        Returns an SSMDao initialized with a session for the next higher environment.
        """
        return SsmDao(self.__next_env().client('ssm'))

    def __ssm(self) -> SsmDao:
        """
        Returns an SSMDao initialized with a session for the selected ENV based on FiggyContext
        """
        if not self._ssm:
            self._ssm = SsmDao(self.__env_session().client('ssm'))

        return self._ssm

    def __kms(self) -> KmsSvc:
        """
        Returns a hydrated KMS Service object based on these selected ENV
        """
        if not self._kms:
            self._kms: KmsSvc = KmsSvc(self.__env_session().client('kms'))

        return self._kms

    def __config(self) -> ConfigDao:
        """
        Returns a hydrated ConfigDao for the selected environment.
        """
        return ConfigDao(self.__env_session().resource('dynamodb'))

    def __mgmt_s3_resource(self):
        """
        Returns a hydrated boto3 S3 Resource for the mgmt account.
        """
        if not self._mgmt_s3_rsc:
            self._mgmt_s3_rsc = self.__mgmt_session().resource('s3')

        return self._mgmt_s3_rsc

    def __all_sessions(self) -> Dict[str, boto3.session.Session]:
        """
        Populates a DICT containing boto sessions for all 4 environments (dev -> prod).
        """
        if not self._all_sessions and self._context.all_profiles:
            self._all_sessions: Dict[str, boto3.session.Session] = {}

            with ThreadPoolExecutor(max_workers=10) as pool:
                session_futures: Dict[str, thread] = {
                    env: pool.submit(self._session_manager.get_session, RunEnv(env),
                                     self._context.selected_role, prompt=False)
                    for env in envs
                }

                for env, future in session_futures.items():
                    self._all_sessions[env] = future.result()
        else:
            self._all_sessions = None

        return self._all_sessions

    def __cache_mgr(self) -> CacheManager:
        """Builds a cache manager service for the specified resource."""
        if not self._cache_mgr:
            self._cache_mgr: CacheManager = CacheManager(Utils.get_first(self._context.resource))

        return self._cache_mgr

    def __config_service(self) -> ConfigService:
        """Returns a hydrated ConfigService."""
        if not self._config_svc:
            self._config_svc = ConfigService(self.__config(), self.__cache_mgr(), self._context.run_env)

        return self._config_svc

    def __config_completer(self):
        """
        This is used to be a slow operation since it involves pulling all parameter names from Parameter Store.
        It's best to be lazy loaded only if the dependent command requires it. It's still best to be lazy loaded,
        but it is much faster now that we have implemented caching of existing parameter names in DynamoDb and
        locally.
        """
        if not self._config_completer:
            all_names = sorted(self.__config_service().get_parameter_names())
            self._config_completer = WordCompleter(all_names, sentence=True, match_middle=True)

        return self._config_completer
        # print(f"Cache Count: {len(all_names)}")

    def instance(self):
        """
        Get an instance of a particular command based on the FiggyContext provided into this factory.
        """
        factory: Factory = None
        start = time.time()

        if self._context.command in config_commands and self._context.resource == config:
            context = ConfigContext(self._context.run_env, self._context.selected_role, self._context.args, config)
            futures = set()

            # Multiple threads to init resources saves 500 - 1000 MS
            with ThreadPoolExecutor(max_workers=5) as pool:
                futures.add(pool.submit(self._ssm))
                futures.add(pool.submit(self.__kms))
                futures.add(pool.submit(self.__mgmt_s3_resource))
                futures.add(pool.submit(self.__next_ssm))

            for future in as_completed(futures):
                pass  # Force lazy init for all futures.

            factory = ConfigFactory(self._context.command, context, self.__ssm(), self.__config(), self.__kms(),
                                    self.__mgmt_s3_resource(), self._context.colors_enabled, self.__config_completer(),
                                    dest_ssm=self.__next_ssm())

        elif self._context.command in iam_commands and self._context.resource == iam:
            context = IAMContext(self._context.run_env, self._context.selected_role, self._context.colors_enabled, iam)
            factory = IAMFactory(self._context.command, context, self.__env_session(), self.__mgmt_session(),
                                 all_sessions=self.__all_sessions())
        else:
            self._utils.error_exit(
                f"Command: {self._utils.get_first(self._context.command)} was not found in this version of figgy.")

        logger.info(f"Init completed in {time.time() - start} seconds.")
        return factory.instance()
