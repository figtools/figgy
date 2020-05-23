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

    def configure_preferences(self, current_defaults: CLIDefaults):
        updated_defaults = current_defaults
        updated_defaults.region = Input.select_region()
        updated_defaults.colors_enabled = Input.select_enable_colors()
        updated_defaults.report_errors = Input.select_report_errors()
        self.save_defaults(updated_defaults)
        return updated_defaults

    def basic_configure(self, configure_provider=True) -> CLIDefaults:
        defaults: CLIDefaults = self.get_defaults()
        if not defaults:
            Utils.stc_error_exit(f"Please run {CLI_NAME} --{Utils.get_first(configure)} to set up Figgy, "
                                 f"you've got problems friend!")
        else:
            defaults = self.configure_auth(defaults, configure_provider=configure_provider)

        self.save_defaults(defaults)
        return defaults

    def configure_auth(self, current_defaults: CLIDefaults, configure_provider=True) -> CLIDefaults:
        updated_defaults = current_defaults

        if configure_provider or current_defaults.provider is Provider.UNSELECTED:
            provider: Provider = Input.select_provider()
            updated_defaults.provider = provider
        else:
            provider: Provider = current_defaults.provider

        if provider in Provider.sso_providers():
            user: str = Input.get_user(provider=provider.name)
            password: str = Input.get_password(provider=provider.name)
            SecretsManager.set_password(user, password)
            updated_defaults.user = user

        if configure_provider:
            provider_config = ProviderConfigFactory().instance(provider, mfa_enabled=current_defaults.mfa_enabled)
            updated_defaults.provider_config = provider_config

        updated_defaults.mfa_enabled = Input.select_mfa_enabled()

        return updated_defaults

    def save_defaults(self, defaults: CLIDefaults):
        self._cache_mgr.write(DEFAULTS_FILE_CACHE_KEY, defaults)

    def get_defaults(self) -> CLIDefaults:
        last_write, defaults = self._cache_mgr.get(DEFAULTS_FILE_CACHE_KEY)
        return defaults if defaults else CLIDefaults.unconfigured()
