import logging
from typing import Callable

from config import *
from input import Input
from models.defaults.defaults import CLIDefaults
from models.defaults.provider import Provider
from models.defaults.provider_config import ProviderConfigFactory
from svcs.cache_manager import CacheManager
from svcs.config_manager import ConfigManager
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
        self._config_mgr, self.c = ConfigManager.figgy(), Utils.default_colors()

    def configure_preferences(self, current_defaults: CLIDefaults):
        updated_defaults = current_defaults
        updated_defaults.region = self._config_mgr.get_or_prompt(Config.Section.Figgy.AWS_REGION, Input.select_region)
        updated_defaults.colors_enabled = self._config_mgr.get_or_prompt(Config.Section.Figgy.COLORS_ENABLED,
                                                                         Input.select_enable_colors)
        updated_defaults.report_errors = self._config_mgr.get_or_prompt(Config.Section.Figgy.REPORT_ERRORS,
                                                                        Input.select_report_errors)
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

        try:
            mfa_enabled = Utils.parse_bool(self._config_mgr.get_or_prompt(Config.Section.Figgy.MFA_ENABLED,
                                                                          Input.select_mfa_enabled))
            if mfa_enabled:
                auto_mfa = self._config_mgr.get_or_prompt(Config.Section.Figgy.AUTO_MFA, Input.select_auto_mfa)
            else:
                auto_mfa = False

        except ValueError as e:
            Utils.stc_error_exit(f"Invalid value found in figgy defaults file under "
                                 f"{Config.Section.Figgy.MFA_ENABLED.value}. It must be either 'true' or 'false'")
        else:
            updated_defaults.mfa_enabled = mfa_enabled
            updated_defaults.auto_mfa = auto_mfa

        if updated_defaults.auto_mfa:
            mfa_secret = Input.get_mfa_secret()
            SecretsManager.set_mfa_secret(updated_defaults.user, mfa_secret)

        if configure_provider:
            provider_config = ProviderConfigFactory().instance(provider, mfa_enabled=updated_defaults.mfa_enabled)
            updated_defaults.provider_config = provider_config

        return updated_defaults

    def save_defaults(self, defaults: CLIDefaults):
        self._cache_mgr.write(DEFAULTS_FILE_CACHE_KEY, defaults)

    def get_defaults(self) -> CLIDefaults:
        try:
            last_write, defaults = self._cache_mgr.get(DEFAULTS_FILE_CACHE_KEY)
        except Exception:
            # If cache is corrupted or inaccessible, "fogetaboutit" (in italian accent)
            return CLIDefaults.unconfigured()

        return defaults if defaults else CLIDefaults.unconfigured()
