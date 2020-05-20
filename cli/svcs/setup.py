import logging
from config import *
from input import Input
from models.defaults.defaults import CLIDefaults
from models.defaults.provider import Provider
from models.defaults.provider_config import ProviderConfigFactory
from svcs.cache_manager import CacheManager
from utils.secrets_manager import SecretsManager
from utils.utils import Utils

log = logging.getLogger(__name__)


class FiggySetup:
    """
    Contains logic around setting up Figgy. Configuring user auth, etc.
    """

    # If we ever need to add params to this constructor we'll need to better handle dependencies and do a bit of
    # refactoring here.
    def __init__(self):
        self._cache_mgr = CacheManager(DEFAULTS_FILE_CACHE_KEY)

    def basic_configure(self) -> CLIDefaults:
        defaults: CLIDefaults = self.get_defaults()
        if not defaults:
            Utils.stc_error_exit(f"Please run {CLI_NAME} --{Utils.get_first(configure)} to set up Figgy, "
                                 f"you've got problems friend!")
        else:
            defaults = self.configure_auth(defaults)

        self.save_defaults(defaults)
        return defaults

    def configure_auth(self, current_defaults: CLIDefaults) -> CLIDefaults:
        updated_defaults = current_defaults
        provider: Provider = Input.select_provider()
        updated_defaults.provider = provider

        if provider in Provider.sso_providers():
            user: str = Input.get_user()
            password: str = Input.get_password()
            SecretsManager.set_password(user, password)
            updated_defaults.user = user

        provider_config = ProviderConfigFactory().instance(provider, mfa_enabled=current_defaults.mfa_enabled)
        updated_defaults.provider_config = provider_config

        return updated_defaults

    def save_defaults(self, defaults: CLIDefaults):
        self._cache_mgr.write(DEFAULTS_FILE_CACHE_KEY, defaults)

    def get_defaults(self) -> CLIDefaults:
        last_write, defaults = self._cache_mgr.get(DEFAULTS_FILE_CACHE_KEY)
        return defaults if defaults else CLIDefaults.unconfigured()
