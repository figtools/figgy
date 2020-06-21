import json
import logging
import os
import uuid
from typing import Set, List, Tuple, Optional

import boto3
from botocore.exceptions import NoCredentialsError, ClientError, ParamValidationError

from figcli.config.constants import *
from figcli.data.dao.ssm import SsmDao
from figcli.input import Input
from figcli.models.assumable_role import AssumableRole
from figcli.models.aws_session import FiggyAWSSession
from figcli.models.defaults.defaults import CLIDefaults
from figcli.models.defaults.provider import Provider
from figcli.models.role import Role
from figcli.models.run_env import RunEnv
from figcli.svcs.cache_manager import CacheManager
from figcli.svcs.auth.provider.session_provider import SessionProvider
from figcli.svcs.vault import FiggyVault
from figcli.utils.secrets_manager import SecretsManager
from figcli.utils.utils import Utils, InvalidSessionError
import time

log = logging.getLogger(__name__)


class BastionSessionProvider(SessionProvider):
    _MAX_ATTEMPTS = 5

    def __init__(self, defaults: CLIDefaults):
        super().__init__(defaults)
        self.__id = uuid.uuid4()
        self._utils = Utils(defaults.colors_enabled)
        self.__bastion_session = boto3.session.Session(profile_name=self._defaults.provider_config.profile_name)
        self._ssm = None
        self._sts = None
        self._iam_client = None
        self._iam = None
        keychain_enabled = defaults.extras.get(DISABLE_KEYRING) is not True
        vault = FiggyVault(keychain_enabled=keychain_enabled)
        self._sts_cache: CacheManager = CacheManager(file_override=STS_SESSION_CACHE_PATH, vault=vault)
        self._role_name_prefix = os.getenv(FIGGY_ROLE_PREFIX_OVERRIDE_ENV, FIGGY_ROLE_NAME_PREFIX)

    def __get_iam_user(self):
        self._defaults.user = self.__get_iam_resource().CurrentUser().user_name
        return self._defaults.user

    def __get_iam_resource(self):
        if not self._iam:
            self._iam = self.__bastion_session.resource('iam')

        return self._iam

    def __get_iam_client(self):
        if not self._iam_client:
            self._iam_client = self.__bastion_session.client('iam')

        return self._iam_client

    def __get_ssm(self):
        if not self._ssm:
            self._ssm = SsmDao(self.__bastion_session.client('ssm'))
        return self._ssm

    def __get_sts(self):
        if not self._sts:
            self._sts = self.__bastion_session.client('sts')
        return self._sts

    def get_mfa_serial(self) -> Optional[str]:
        response = self.__get_iam_client().list_mfa_devices(UserName=self._defaults.user)
        devices = response.get('MFADevices', [])
        log.info(f'Found MFA devices: {devices}.')
        return devices[0].get('SerialNumber') if devices else None

    def get_session(self, assumable_role: AssumableRole, prompt: bool, exit_on_fail=True) -> boto3.Session:
        forced = False
        log.info(f"Getting session for role: {assumable_role.role_arn} in env: {assumable_role.run_env.env}")
        attempts = 0
        while True:
            try:
                if prompt and not forced:
                    forced = True
                    raise InvalidSessionError("Forcing new session due to prompt.")

                creds: FiggyAWSSession = self._sts_cache.get_val(assumable_role.role.full_name)

                if creds:
                    session = boto3.Session(
                        aws_access_key_id=creds.access_key,
                        aws_secret_access_key=creds.secret_key,
                        aws_session_token=creds.token,
                        region_name=self._defaults.region
                    )

                    if not self._is_valid_session(session):
                        self._utils.validate(attempts < self._MAX_ATTEMPTS,
                                             f"Failed to authenticate with AWS after {attempts} attempts. Exiting. ")

                        attempts = attempts + 1
                        log.info("Invalid session detected in cache. Raising session error.")
                        raise InvalidSessionError("Invalid Session Detected")

                    log.info("Valid session returned from cache.")
                    return session
                else:
                    raise InvalidSessionError("Forcing new session, cache is empty.")
            except (FileNotFoundError, NoCredentialsError, InvalidSessionError) as e:
                try:
                    if self._defaults.mfa_enabled:
                        self._defaults.mfa_serial = self.get_mfa_serial()
                        color = Utils.default_colors() if self._defaults.colors_enabled else None
                        mfa = SecretsManager.generate_mfa(self._defaults.user) if self._defaults.auto_mfa else \
                                                            Input.get_mfa(display_hint=True, color=color)

                        response = self.__get_sts().assume_role(RoleArn=assumable_role.role_arn,
                                                                RoleSessionName=Utils.sanitize_session_name(
                                                                    self._defaults.user),
                                                                DurationSeconds=self._defaults.session_duration,
                                                                SerialNumber=self._defaults.mfa_serial,
                                                                TokenCode=mfa)
                    else:
                        response = self.__get_sts().assume_role(RoleArn=assumable_role.role_arn,
                                                                RoleSessionName=Utils.sanitize_session_name(
                                                                    self._defaults.user),
                                                                DurationSeconds=self._defaults.session_duration)

                    session = FiggyAWSSession.from_sts_response(response)
                    log.info(f"Got session response: {response}")
                    self._sts_cache.write(assumable_role.role.full_name, session)
                except (ClientError, ParamValidationError) as e:
                    if isinstance(e, ParamValidationError) or "AccessDenied" == e.response['Error']['Code']:
                        if exit_on_fail:
                            self._utils.error_exit(f"Error authenticating with AWS from Bastion Profile:"
                                                   f" {self._defaults.provider_config.profile_name}: {e}")
                    else:
                        if exit_on_fail:
                            log.error(f"Failed to authenticate due to error: {e}")
                            self._utils.error_exit(
                                f"Error getting session for role: {assumable_role.role_arn} "
                                f"-- Are you sure you have permissions?")

                    raise e

    def get_assumable_roles(self):
        if self.is_role_session():
            user_roles = [self._defaults.role.role]
        else:
            ROLE_PATH = f'/figgy/users/{self.__get_iam_user()}/roles'
            user_roles = self.__get_ssm().get_parameter(ROLE_PATH)
            self._utils.stc_validate(user_roles is not None and user_roles != "[]",
                                     "Something is wrong with your user's configuration with Figgy. "
                                     "Unable to find any eligible roles for your user. Please contact your"
                                     " administrator.")

            user_roles = json.loads(user_roles)

        environments = self.__get_ssm().get_all_parameters([PS_FIGGY_ACCOUNTS_PREFIX], option='OneLevel')
        names: List[str] = [env.get('Name') for env in environments]
        parameters = self.__get_ssm().get_parameter_values(names)
        assumable_roles: List[AssumableRole] = []

        for param in parameters:
            env_name = param.get('Name').split('/')[-1]
            account_id = param.get('Value')

            for role in user_roles:
                assumable_roles.append(AssumableRole(
                    run_env=RunEnv(env=env_name, account_id=account_id),
                    role=Role(role, full_name=f'{FIGGY_ROLE_NAME_PREFIX}{env_name}-{role}'),
                    account_id=account_id,
                    provider_name=Provider.AWS_BASTION.value,
                    profile=None
                ))

        return assumable_roles

    def is_role_session(self):
        """
        For sandbox demos, where users aren't coming from user accounts, we want to skip looking up user -> role.
        :return: bool - Is this session originating from a role?
        """
        creds = self.__bastion_session.get_credentials().get_frozen_credentials()

        return hasattr(creds, 'token') and creds.token is not None

    def cleanup_session_cache(self):
        self._sts_cache.wipe_cache()
