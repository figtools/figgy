import base64
import logging
import re
import xml.etree.ElementTree as ET
from abc import ABC
from json import JSONDecodeError
from typing import List
from figcli.config import *
from figcli.input import Input
from figcli.models.assumable_role import AssumableRole
from figcli.models.defaults.defaults import CLIDefaults
from figcli.models.role import Role
from figcli.models.run_env import RunEnv
from figcli.models.sso.okta.okta_primary_auth import OktaPrimaryAuth, OktaSession
from figcli.models.sso.okta.okta_session_auth import OktaSessionAuth
from figcli.svcs.cache_manager import CacheManager
from figcli.svcs.auth.okta.okta import Okta, InvalidSessionError
from figcli.svcs.auth.provider.sso_session_provider import SSOSessionProvider
from figcli.svcs.vault import FiggyVault
from figcli.utils.secrets_manager import SecretsManager
from figcli.utils.utils import Utils

log = logging.getLogger(__name__)


class OktaSessionProvider(SSOSessionProvider, ABC):
    _SESSION_CACHE_KEY = 'session'

    def __init__(self, defaults: CLIDefaults):
        super().__init__(defaults)
        keychain_enabled = defaults.extras.get(DISABLE_KEYRING) is not True
        vault = FiggyVault(keychain_enabled=keychain_enabled)
        self._cache_manager: CacheManager = CacheManager(file_override=OKTA_SESSION_CACHE_PATH, vault=vault)
        self._saml_cache: CacheManager = CacheManager(file_override=SAML_SESSION_CACHE_PATH, vault=vault)

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
        count = 0
        while True:
            try:
                if prompt:
                    raise InvalidSessionError("Forcing new session due to prompt.")

                cached_session = self._get_session_from_cache()
                if not cached_session:
                    raise InvalidSessionError

                okta = Okta(OktaSessionAuth(cached_session))
                return okta
            except (FileNotFoundError, InvalidSessionError, JSONDecodeError, AttributeError) as e:
                try:
                    password = SecretsManager.get_password(self._defaults.user)
                    if self._defaults.mfa_enabled:
                        color = Utils.default_colors() if self._defaults.colors_enabled else None
                        mfa = SecretsManager.generate_mfa(self._defaults.user) if self._defaults.auto_mfa else\
                                Input.get_mfa(display_hint=True, color=color)
                    else:
                        mfa = None
                    primary_auth = OktaPrimaryAuth(self._defaults, password, mfa)
                    self._write_okta_session_to_cache(primary_auth.get_session())
                    return Okta(primary_auth)
                except InvalidSessionError as e:
                    count += 1
                    prompt = True
                    log.error(f"Caught error when authing with OKTA & caching session: {e}. ")
                    if count > 3:
                        Utils.stc_error_exit("Unable to autheticate with OKTA with your provided credentials. Perhaps your"
                                         f"user, password, or MFA changed? Try reunning `{CLI_NAME} --configure` again.")
                    # self._defaults = self._setup.basic_configure(configure_provider=self._defaults.provider_config is None)

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
                password = self._get_password(user, prompt=prompt, save=True)

                if self._defaults.mfa_enabled:
                    color = Utils.default_colors() if self._defaults.colors_enabled else None
                    mfa = SecretsManager.generate_mfa(user) if self._defaults.auto_mfa else \
                        Input.get_mfa(display_hint=True, color=color)
                else:
                    mfa = None

                primary_auth = OktaPrimaryAuth(self._defaults, password, mfa)

                try:
                    log.info("Trying to write session to cache...")
                    self._write_okta_session_to_cache(primary_auth.get_session())
                except InvalidSessionError as e:
                    log.info(f"Got invalid session: {e}")
                    return self.get_saml_assertion(prompt=True)
                else:
                    return self.get_saml_assertion(prompt=True)
            else:
                assertion = base64.b64decode(assertion).decode('utf-8')
                self._saml_cache.write(SAML_ASSERTION_CACHE_KEY, assertion)
                return assertion

    def get_assumable_roles(self) -> List[AssumableRole]:
        return self._cache_manager.get_val_or_refresh('assumable_roles', refresher=self.__lookup_roles)

    def __lookup_roles(self) -> List[AssumableRole]:
        assertion = self.get_saml_assertion(prompt=False)
        root = ET.fromstring(assertion)
        prefix_map = {"saml2": "urn:oasis:names:tc:SAML:2.0:assertion"}
        role_attribute = root.find(".//saml2:Attribute[@Name='https://aws.amazon.com/SAML/Attributes/Role']",
                                   prefix_map)

        # SAML arns should look something like this:
        # arn:aws:iam::106481321259:saml-provider/okta,arn:aws:iam::106481321259:role/figgy-dev-data
        pattern = r'^arn:aws:iam::([0-9]+):saml-provider/(\w+),arn:aws:iam::.*role/(\w+-(\w+)-(\w+))'
        assumable_roles: List[AssumableRole] = []
        for value in role_attribute.findall('.//saml2:AttributeValue', prefix_map):
            result = re.search(pattern, value.text)
            unparsable_msg = f'{value.text} is of an invalid pattern, it must match: {pattern} for figgy to ' \
                             f'dynamically map account_id -> run_env -> role for OKTA users.'
            if not result:
                Utils.stc_error_exit(unparsable_msg)

            result.groups()
            account_id, provider_name, role_name, run_env, role = result.groups()

            if not account_id or not run_env or not role_name or not role:
                Utils.stc_error_exit(unparsable_msg)
            else:
                assumable_roles.append(AssumableRole(account_id=account_id,
                                                     role=Role(role, full_name=role_name),
                                                     run_env=RunEnv(run_env),
                                                     provider_name=provider_name,
                                                     profile=None))
        return assumable_roles

    def cleanup_session_cache(self):
        self._write_okta_session_to_cache(OktaSession("", ""))
