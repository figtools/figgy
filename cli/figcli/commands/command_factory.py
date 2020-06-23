import boto3
import time
import logging
import uuid

from figcli.commands.config_context import ConfigContext
from figcli.commands.config_factory import ConfigFactory
from figcli.commands.help_context import HelpContext
from figcli.commands.help_factory import HelpFactory
from figcli.commands.iam_context import IAMContext
from figcli.commands.iam_factory import IAMFactory
from figcli.commands.factory import Factory
from figcli.models.defaults.defaults import CLIDefaults
from figcli.models.run_env import RunEnv
from figcli.commands.figgy_context import FiggyContext
from figcli.svcs.kms import KmsSvc
from figcli.svcs.config import ConfigService
from figcli.svcs.cache_manager import CacheManager
from figcli.svcs.auth.provider.provider_factory import SessionProviderFactory
from figcli.svcs.auth.provider.session_provider import SessionProvider
from figcli.svcs.auth.session_manager import SessionManager
from figcli.data.dao.config import ConfigDao
from figcli.utils.utils import Utils
from figcli.config import *
from figcli.data.dao.ssm import SsmDao
from typing import Dict
from concurrent.futures import ThreadPoolExecutor, thread, as_completed

from figcli.views.rbac_limited_config import RBACLimitedConfigView
from threading import Lock
logger = logging.getLogger(__name__)


class CommandFactory(Factory):
    """
    Uses the provided FiggyContext (which contains details of args passed in, etc), and initializes a command
    factory of the appropriate type, and generates the appropriate command.
    """

    def __init__(self, context: FiggyContext, cli_defaults: CLIDefaults):
        self._id = uuid.uuid4()
        self._context = context
        self._utils = Utils(context.colors_enabled)
        self._cli_defaults = cli_defaults
        self._session_mgr = None
        self._session_provider = None
        self._env_session = None
        self._ssm = None
        self._config = None
        self._kms = None
        self._s3_rsc = None
        self._all_sessions = None
        self._config_svc = None
        self._cache_mgr = None
        self._rbac_config_view = None
        self.__env_lock = Lock()
        self.__mgr_lock = Lock()

    def __session_provider(self) -> SessionProvider:
        if not self._session_provider:
            self._session_provider = SessionProviderFactory(self._cli_defaults).instance()

        return self._session_provider

    def __session_manager(self):
        """
        Lazy load the session manager, only create a session if this command requires it.
        :return: 
        """
        with self.__mgr_lock:
            if not self._session_mgr:
                self._session_mgr = SessionManager(self._cli_defaults, self.__session_provider())

        return self._session_mgr

    def __env_session(self) -> boto3.session.Session:
        """
        Lazy load an ENV session object for the ENV selected in the FiggyContext
        :return: Hydrated session for the selected environment.
        """
        with self.__env_lock:
            if not self._env_session:
                self._env_session = self.__session_manager().get_session(
                    self._context.selected_role,
                    prompt=False)

        return self._env_session

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

    def __s3_resource(self):
        """
        Returns a hydrated boto3 S3 Resource for the mgmt account.
        """
        if not self._s3_rsc:
            self._s3_rsc = self.__env_session().resource('s3')

        return self._s3_rsc

    def __all_sessions(self) -> Dict[str, boto3.session.Session]:
        """
        Populates a DICT containing boto sessions for all 4 environments (dev -> prod).
        """
        assumable_roles = self._cli_defaults.assumable_roles
        matching_roles = list(set([x for x in assumable_roles if x.role == self._context.role]))

        if not self._all_sessions and self._context.all_profiles:
            self._all_sessions: Dict[str, boto3.session.Session] = {}

            with ThreadPoolExecutor(max_workers=10) as pool:
                session_futures: Dict[str, thread] = {
                    role.role.full_name: pool.submit(self.__session_manager().get_session, role, prompt=False)
                    for role in matching_roles
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

    def __rbac_config_view(self) -> RBACLimitedConfigView:
        if not self._rbac_config_view:
            self._rbac_config_view = RBACLimitedConfigView(self._context.role, self.__cache_mgr(),
                                                           self.__ssm(), self.__config_service())
        return self._rbac_config_view

    def __init_sessions(self):
        """
        Bootstraps sessions (blocking) before we do threaded lookups that require these sessions.
        """
        self.__session_manager().get_session(
                self._context.selected_role,
                prompt=False)

    def instance(self):
        """
        Get an instance of a particular command based on the FiggyContext provided into this factory.
        """
        factory: Factory = None
        start = time.time()

        if self._context.command in config_commands and self._context.resource == config:
            self.__init_sessions()
            context = ConfigContext(self._context.run_env, self._context.role, self._context.args, config,
                                    defaults=self._cli_defaults)


            futures = set()
            # Multiple threads to init resources saves 500 - 1000 MS
            with ThreadPoolExecutor(max_workers=5) as pool:
                futures.add(pool.submit(self._ssm))
                futures.add(pool.submit(self.__kms))
                futures.add(pool.submit(self.__s3_resource))

            for future in as_completed(futures):
                pass  # Force lazy init for all futures.

            factory = ConfigFactory(self._context.command, context, self.__ssm(), self.__config(), self.__kms(),
                                    self.__s3_resource(), self._context.colors_enabled, self.__rbac_config_view(),
                                    self.__session_manager())

        elif self._context.command in iam_commands and self._context.resource == iam:
            self.__init_sessions()
            context = IAMContext(self._context.run_env, self._context.role, self._context.colors_enabled, iam,
                                 defaults=self._cli_defaults)
            factory = IAMFactory(self._context.command, context, self.__env_session(),
                                 all_sessions=self.__all_sessions())
        elif self._context.find_matching_optional_arguments(help_commands) or self._context.resource in help_commands:
            optional_args = self._context.find_matching_optional_arguments(help_commands)
            context = HelpContext(self._context.resource, self._context.command, optional_args, self._context.run_env,
                                  defaults=self._cli_defaults)
            factory = HelpFactory(self._context.command, context)
        else:
            if self._context.command is None or self._context.resource:
                self._utils.error_exit(f"Proper {CLI_NAME} syntax is `{CLI_NAME} <resource> <command> --options`. "
                                       f"For example `{CLI_NAME} config get`. Either resource or command were "
                                       f"not supplied.")
            else:
                self._utils.error_exit(
                    f"Command: {self._utils.get_first(self._context.command)} was not found in this version of figgy.")

        logger.info(f"Init completed in {time.time() - start} seconds.")
        return factory.instance()
