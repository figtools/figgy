import os
from json import JSONDecodeError

import boto3
import logging
import json
from abc import ABC, abstractmethod

from botocore.exceptions import NoCredentialsError, ParamValidationError, ClientError

from config import *
from models.assumable_role import AssumableRole
from models.defaults.defaults import CLIDefaults
from svcs.sso.provider.session_provider import SessionProvider
from utils.utils import InvalidSessionError, Utils

log = logging.getLogger(__name__)


class SSOSessionProvider(SessionProvider, ABC):
    _MAX_ATTEMPTS = 5

    def __init__(self, defaults: CLIDefaults):
        super().__init__(defaults)
        self._utils = Utils(defaults.colors_enabled)
        self._sts = boto3.client('sts')

    @abstractmethod
    def cleanup_session_cache(self):
        pass

    @abstractmethod
    def get_saml_assertion(self, prompt: bool = False):
        pass

    def get_session(self, assumable_role: AssumableRole, prompt: bool, exit_on_fail=True) -> boto3.Session:
        """
        Creates a session in the specified ENV for the target role from a SAML assertion returned by OKTA authentication.
        Args:
            assumable_role: AssumableRole - The role to be leveraged to authenticate this session
            prompt: If prompt is set, we will not use a cached session and will generate new sessions for okta and mgmt.
            exit_on_fail: Exit the program if this session hydration fails.

        returns: Hydrated session for role + account that match the specified one in the provided AssumableRole
        """

        role_arn = f"arn:aws:iam::{assumable_role.account_id}:role/{assumable_role.role.full_name}"
        cache_path = f"{HOME}/.figgy/devops/cache/sts/{assumable_role.role.full_name}"
        principal_arn = f"arn:aws:iam::{assumable_role.account_id}:saml-provider/{OKTA_PROVIDER_NAME}"
        forced = False

        log.info(f"Getting session for role: {role_arn} in env: {env}")
        attempts = 0
        while True:
            try:
                os.makedirs(os.path.dirname(cache_path), exist_ok=True)

                if prompt and not forced:
                    forced = True
                    raise InvalidSessionError("Forcing new session due to prompt.")

                log.info(f"Reading from cache: {cache_path}")
                with open(cache_path, "r") as cache:
                    contents = cache.read()
                    response = json.loads(contents)
                    session = boto3.Session(
                        aws_access_key_id=response['Credentials']['AccessKeyId'],
                        aws_secret_access_key=response['Credentials']['SecretAccessKey'],
                        aws_session_token=response['Credentials']['SessionToken'],
                        region_name=AWS_REGION
                    )

                if not self._is_valid_session(session):
                    self._utils.validate(attempts < self._MAX_ATTEMPTS,
                                         f"Failed to authenticate with OKTA/AWS after {attempts} attempts. Exiting. ")

                    attempts = attempts + 1
                    log.info("Invalid session detected in cache. Raising session error.")
                    raise InvalidSessionError("Invalid Session Detected")

                return session
            except (FileNotFoundError, JSONDecodeError, NoCredentialsError, InvalidSessionError) as e:
                try:
                    assertion = self.get_saml_assertion(prompt)
                    response = self._sts.assume_role_with_saml(RoleArn=role_arn,
                                                               PrincipalArn=principal_arn,
                                                               SAMLAssertion=assertion,
                                                               DurationSeconds=ENV_SESSION_DURATION)
                    log.info(f"Got session response: {response}")
                    response['Credentials']['Expiration'] = "cleared"
                    with open(cache_path, "w") as cache:
                        log.info("Writing new session to cache.")
                        cache.write(json.dumps(response))
                except (ClientError, ParamValidationError) as e:
                    if isinstance(e, ParamValidationError) or "AccessDenied" == e.response['Error']['Code']:
                        if exit_on_fail:
                            self._utils.error_exit(f"Error authenticating with AWS from OKTA SAML Assertion: {e}")
                    else:
                        if exit_on_fail:
                            self._utils.error_exit(
                                f"Error getting OKTA session for role: {role_arn} -- Are you sure you have permissions?")

                    raise e
