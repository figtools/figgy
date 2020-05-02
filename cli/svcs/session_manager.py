import json
import logging
import os
import boto3

from botocore.errorfactory import ClientError
from botocore.exceptions import NoCredentialsError, ParamValidationError
from json import JSONDecodeError
from input import *
from config import *
from models.defaults import CLIDefaults
from models.okta_config import OktaConfig
from models.okta_primary_auth import OktaPrimaryAuth
from models.okta_session_auth import OktaSessionAuth
from models.role import Role
from models.run_env import RunEnv
from svcs.okta import Okta
from utils.secrets_manager import SecretsManager
from utils.utils import Utils, InvalidSessionError

log = logging.getLogger(__name__)


class SessionManager:
    _MAX_ATTEMPTS = 5

    def __init__(self, colors_enabled: bool, defaults: CLIDefaults):
        self._sts = boto3.client('sts')
        self._utils = Utils(colors_enabled)
        self._defaults = defaults
        self._okta = self._get_okta(False)
        self._failure_count = 0

    @Utils.retry
    @Utils.trace
    def _is_valid_session(self, session: boto3.Session):
        """Tests whether a cached session is valid or not."""
        try:
            sts = session.client('sts')
            sts.get_caller_identity()
            return True
        except ClientError:
            return False

    def _write_okta_session_to_cache(self, session: str) -> None:
        with open(OKTA_SESSION_CACHE_PATH, "w") as cache:
            cache.write(session)

    # @Utils.trace
    def _get_okta(self, prompt: bool) -> Okta:
        """
        Pulls the last okta session from cache, if cache doesn't exist, generates a new session and writes it to cache.
        From this session, the OKTA SVC is hydrated and returned.
        Args:
            prompt: If supplied, will never get session from cache.

        Returns: Initialized Okta service.
        """
        cache_path = f"{HOME}/.figgy/devops/cache/okta/session"
        while True:
            try:
                os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                if prompt:
                    raise InvalidSessionError("Forcing new session due to prompt.")

                with open(cache_path, "r") as cache:
                    contents = json.loads(cache.read())
                    session_token = contents[OKTA_SESSION_TOKEN_CACHE_KEY]
                    session_id = contents[OKTA_SESSION_ID_CACHE_KEY]
                    okta = Okta(OktaConfig(OktaSessionAuth(session_token, session_id)))
                    return okta

            except (FileNotFoundError, InvalidSessionError, JSONDecodeError, AttributeError) as e:
                try:
                    user = self._get_okta_user(prompt)
                    password = self._get_okta_password(user, prompt)
                    primary_auth = OktaPrimaryAuth(user, password, Input.get_okta_mfa())
                    print("I AM HERE")
                    self._write_okta_session_to_cache(primary_auth.to_json())

                    return Okta(OktaConfig(primary_auth))
                except InvalidSessionError as e:
                    log.error(f"Caught error when authing with OKTA & caching session: {e}")
                    print("Authentication failed with OKTA, please reauthenticate. Likely invalid MFA or Password?\r\n")

    def _get_okta_user(self, prompt: bool) -> str:
        """
        Get the OKTA user either from cache, or prompt the user.

        Returns: str -> username
        """

        defaults = self._defaults
        if defaults is not None and not prompt:
            return defaults.okta_user
        else:
            return Input.get_okta_user()

    def _get_okta_password(self, user_name, prompt: bool, save: bool = False) -> str:
        """
        Get the OKTA pw either from keyring, or prompt the user.

        Returns: str -> password
        """

        password = SecretsManager.get_password(user_name)
        reset_password = not password

        if reset_password or prompt:
            password = Input.get_okta_password()
            if reset_password or save:
                SecretsManager.set_password(user_name, password)

        return password

    #Todo: Perhaps cache the last assertion?
    @Utils.trace
    def _get_okta_assertion(self, prompt: bool = False) -> str:
        """
        Lookup OKTA session from cache, if it's valid, use it, otherwise, generate new assertion with MFA
        Args:
            prompt: Used for forcing prompts of username / password and always generating a new assertion
            force_new: Forces a new session, abandons one from cache
        """
        invalid_session = True
        while invalid_session:
            try:
                assertion = self._okta.get_assertion()
            except InvalidSessionError as e:
                if self._failure_count > 0:
                    print(e)
                    print("Authentication failed with OKTA, please reauthenticate. Likely invalid MFA or Password?\r\n")

                self._failure_count = self._failure_count + 1
                log.info(f"GOT INVALID SESSION: {e}")
                user = self._get_okta_user(prompt)
                primary_auth = OktaPrimaryAuth(user,
                                               self._get_okta_password(user, prompt=prompt, save=True),
                                               Input.get_okta_mfa())

                self._okta = Okta(OktaConfig(primary_auth))
                try:
                    log.info("Trying to write session to cache...")
                    self._write_okta_session_to_cache(primary_auth.to_json())
                except InvalidSessionError as e:
                    log.info(f"GOt invalid session: {e}")
                    return self._get_okta_assertion(prompt=True)
                else:
                    return self._get_okta_assertion(prompt=True)
            else:
                return assertion

    @Utils.trace
    def get_session(self, env: RunEnv, role: Role, prompt: bool, exit_on_fail=True) -> boto3.Session:
        """
        Creates a session in the specified ENV for the target role from a SAML assertion returned by OKTA authentication.
        Args:
            env: RunEnv - the ENV you want a session for.
            role: Role - the Role you need access to in that ENV
            prompt: If prompt is set, we will not use a cached session and will generate new sessions for okta and mgmt.
            exit_on_fail: Exit the program if this session hydration fails.

        Returns: hydrated boto3.session in the MGMT account. This role is used to jump into other roles.
        """

        role_arn = f'{ROLE_ARN_MAP[env.env]}figgy-{role.role}'
        cache_path = f"{HOME}/.figgy/devops/cache/sts/{env.env}-{role.role}"
        principal_arn = f"arn:aws:iam::{ACCOUNT_ID_MAP[env.env]}:saml-provider/{OKTA_PROVIDER_NAME}"
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
                    assertion = self._get_okta_assertion(prompt)
                    log.info(f"Got SAML assersion: {assertion}")

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
