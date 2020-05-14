import base64
import logging
import re
import xml.etree.ElementTree as ET
from abc import ABC
from json import JSONDecodeError
from typing import List
from config import *
from input import Input
from models.assumable_role import AssumableRole
from models.defaults.defaults import CLIDefaults
from models.role import Role
from models.run_env import RunEnv
from models.sso.okta.okta_config import OktaConfig
from models.sso.okta.okta_primary_auth import OktaPrimaryAuth, OktaSession
from models.sso.okta.okta_session_auth import OktaSessionAuth
from svcs.cache_manager import CacheManager
from svcs.setup import FiggySetup
from svcs.sso.okta.okta import Okta, InvalidSessionError
from svcs.sso.provider.sso_session_provider import SSOSessionProvider
from utils.secrets_manager import SecretsManager
from utils.utils import Utils

log = logging.getLogger(__name__)


class OktaSessionProvider(SSOSessionProvider, ABC):
    _SESSION_CACHE_KEY = 'session'

    def __init__(self, defaults: CLIDefaults):
        super().__init__(defaults)
        self._cache_manager: CacheManager = CacheManager(file_override=OKTA_SESSION_CACHE_PATH)
        self._setup: FiggySetup = FiggySetup()

    def _write_okta_session_to_cache(self, session: OktaSession) -> None:
        self._cache_manager.write(self._SESSION_CACHE_KEY, session)

    def _get_session_from_cache(self) -> OktaSession:
        last_write, session = self._cache_manager.get(self._SESSION_CACHE_KEY)
        return session

    def get_sso_session(self, prompt: bool = False) -> Okta:
        """
        Pulls the last okta session from cache, if cache doesn't exist, generates a new session and writes it to cache.
        From this session, the OKTA SVC is hydrated and returned.
        Args:
            prompt: If supplied, will never get session from cache.

        Returns: Initialized Okta service.
        """
        while True:
            try:
                if prompt:
                    raise InvalidSessionError("Forcing new session due to prompt.")

                cached_session = self._get_session_from_cache()
                if not cached_session:
                    raise InvalidSessionError

                okta = Okta(OktaConfig(OktaSessionAuth(cached_session)))
                return okta

            except (FileNotFoundError, InvalidSessionError, JSONDecodeError, AttributeError) as e:
                try:
                    password = SecretsManager.get_password(self._defaults.user)
                    primary_auth = OktaPrimaryAuth(self._defaults.user, password, Input.get_mfa())
                    self._write_okta_session_to_cache(primary_auth.get_session())
                    return Okta(OktaConfig(primary_auth))
                except InvalidSessionError as e:
                    log.error(f"Caught error when authing with OKTA & caching session: {e}")
                    print("Authentication failed with OKTA, please reauthenticate. Likely invalid MFA or Password?\r\n")
                    self._defaults = self._setup.basic_configure()
                    prompt = True

    @Utils.trace
    def get_saml_assertion(self, prompt: bool = False) -> str:
        """
        Lookup OKTA session from cache, if it's valid, use it, otherwise, generate new assertion with MFA
        Args:
            prompt: Used for forcing prompts of username / password and always generating a new assertion
            force_new: Forces a new session, abandons one from cache
        """
        invalid_session = True
        okta = self.get_sso_session(prompt)
        failure_count = 0
        while invalid_session:
            try:
                assertion = okta.get_assertion()
            except InvalidSessionError as e:
                if failure_count > 0:
                    print(e)
                    print("Authentication failed with SSO provider, please reauthenticate"
                          " Likely invalid MFA or Password?\r\n")
                    failure_count += 1

                log.info(f"GOT INVALID SESSION: {e}")
                user = self._get_user(prompt)
                primary_auth = OktaPrimaryAuth(user,
                                               self._get_password(user, prompt=prompt, save=True),
                                               Input.get_mfa())

                try:
                    log.info("Trying to write session to cache...")
                    self._write_okta_session_to_cache(primary_auth.get_session())
                except InvalidSessionError as e:
                    log.info(f"Got invalid session: {e}")
                    return self.get_saml_assertion(prompt=True)
                else:
                    return self.get_saml_assertion(prompt=True)
            else:
                return assertion

    def get_assumable_roles(self) -> List[AssumableRole]:
        assertion = self.get_saml_assertion(prompt=True)
        decoded_assertion = base64.b64decode(assertion).decode('utf-8')
        root = ET.fromstring(decoded_assertion)
        prefix_map = {"saml2": "urn:oasis:names:tc:SAML:2.0:assertion"}
        role_attribute = root.find(".//saml2:Attribute[@Name='https://aws.amazon.com/SAML/Attributes/Role']",
                                   prefix_map)

        # SAML arns should look something like this:
        # arn:aws:iam::106481321259:saml-provider/OKTA,arn:aws:iam::106481321259:role/figgy-dev-data
        pattern = r'^arn:aws:iam::([0-9]+):saml-provider/\w+,arn:aws:iam::.*role/(\w+-(\w+)-(\w+))'
        assumable_roles: List[AssumableRole] = []
        for value in role_attribute.findall('.//saml2:AttributeValue', prefix_map):
            result = re.search(pattern, value.text)
            unparsable_msg = f'{value.text} is of an invalid pattern, it must match: {pattern} for figgy to ' \
                             f'dynamically map account_id -> run_env -> role for OKTA users.'
            if not result:
                Utils.stc_error_exit(unparsable_msg)

            result.groups()
            account_id, role_name, run_env, role = result.groups()

            if not account_id or not run_env or not role_name or not role:
                Utils.stc_error_exit(unparsable_msg)
            else:
                assumable_roles.append(AssumableRole(account_id=account_id,
                                                     role=Role(role, full_name=role_name),
                                                     run_env=RunEnv(run_env)))
        return assumable_roles

    def cleanup_session_cache(self):
        self._write_okta_session_to_cache(OktaSession("", ""))
