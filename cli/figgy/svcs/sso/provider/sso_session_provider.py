import os
from json import JSONDecodeError

import boto3
import logging
import base64
import json
from abc import ABC, abstractmethod

from botocore.exceptions import NoCredentialsError, ParamValidationError, ClientError

from figgy.config import *
from figgy.models.assumable_role import AssumableRole
from figgy.models.aws_session import FiggyAWSSession
from figgy.models.defaults.defaults import CLIDefaults
from figgy.svcs.cache_manager import CacheManager
from figgy.svcs.sso.provider.session_provider import SessionProvider
from figgy.svcs.vault import FiggyVault
from figgy.utils.secrets_manager import SecretsManager
from figgy.utils.utils import InvalidSessionError, Utils

log = logging.getLogger(__name__)


class SSOSessionProvider(SessionProvider, ABC):
    _MAX_ATTEMPTS = 5

    def __init__(self, defaults: CLIDefaults):
        super().__init__(defaults)
        self._utils = Utils(defaults.colors_enabled)
        self._sts = boto3.client('sts')
        vault = FiggyVault(SecretsManager.get_password(defaults.user))
        self._sts_cache: CacheManager = CacheManager(file_override=STS_SESSION_CACHE_PATH, vault=vault)
        self._saml_cache: CacheManager = CacheManager(file_override=SAML_SESSION_CACHE_PATH, vault=vault)

    @abstractmethod
    def cleanup_session_cache(self):
        pass

    @abstractmethod
    def get_saml_assertion(self, prompt: bool = False):
        pass

    def get_session(self, assumable_role: AssumableRole, prompt: bool, exit_on_fail=True) -> boto3.Session:
        """
        Creates a session in the specified ENV for the target role from a SAML assertion returned by SSO authentication.
        Args:
            assumable_role: AssumableRole - The role to be leveraged to authenticate this session
            prompt: If prompt is set, we will not use a cached session and will generate new sessions for okta and mgmt.
            exit_on_fail: Exit the program if this session hydration fails.

        returns: Hydrated session for role + account that match the specified one in the provided AssumableRole
        """

        role_arn = f"arn:aws:iam::{assumable_role.account_id}:role/{assumable_role.role.full_name}"
        principal_arn = f"arn:aws:iam::{assumable_role.account_id}:saml-provider/{assumable_role.provider_name}"
        forced = False
        log.info(f"Getting session for role: {role_arn} in env: {assumable_role.run_env.env} "
                 f"with principal: {principal_arn}")
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
            except (FileNotFoundError, JSONDecodeError, NoCredentialsError, InvalidSessionError) as e:
                try:
                    # Todo Remove requiring raw saml and instead work with b64 encoded saml?
                    try:
                        assertion: str = self._saml_cache.get_val_or_refresh(SAML_ASSERTION_CACHE_KEY,
                                                                             self.get_saml_assertion, prompt,
                                                                             max_age=SAML_ASSERTION_MAX_AGE)
                        encoded_assertion = base64.b64encode(assertion.encode('utf-8')).decode('utf-8')
                        response = self._sts.assume_role_with_saml(RoleArn=role_arn,
                                                                   PrincipalArn=principal_arn,
                                                                   SAMLAssertion=encoded_assertion)
                    except ClientError:
                        log.info("Refreshing SAML assertion, auth failed with cached or refreshed version.")
                        assertion = self.get_saml_assertion(prompt)
                        encoded_assertion = base64.b64encode(assertion.encode('utf-8')).decode('utf-8')
                        response = self._sts.assume_role_with_saml(RoleArn=role_arn,
                                                                   PrincipalArn=principal_arn,
                                                                   SAMLAssertion=encoded_assertion)

                    response['Credentials']['Expiration'] = "cleared"
                    session = FiggyAWSSession.from_sts_response(response)
                    self._saml_cache.write(SAML_ASSERTION_CACHE_KEY, assertion)
                    log.info(f"Got session response: {response}")
                    self._sts_cache.write(assumable_role.role.full_name, session)
                except (ClientError, ParamValidationError) as e:
                    if isinstance(e, ParamValidationError) or "AccessDenied" == e.response['Error']['Code']:
                        if exit_on_fail:
                            self._utils.error_exit(f"Error authenticating with AWS from SAML Assertion: {e}")
                    else:
                        if exit_on_fail:
                            print(e)
                            self._utils.error_exit(
                                f"Error getting session for role: {role_arn} -- Are you sure you have permissions?")

                    raise e
