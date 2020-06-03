from abc import ABC, abstractmethod
from dataclasses import dataclass

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

from figgy.config import Config, CONFIG_OVERRIDE_FILE_PATH, SUPPORTED_OKTA_FACTOR_TYPES
from figgy.input.input import Input, List
from figgy.svcs.config_manager import ConfigManager
from figgy.utils.utils import Utils, Color

from figgy.models.defaults.provider import Provider
import re


class ProviderConfig(ABC):

    @staticmethod
    @abstractmethod
    def configure(mfa_enabled: bool = False) -> "ProviderConfig":
        pass


class ProviderConfigFactory:
    @staticmethod
    def instance(provider: Provider, mfa_enabled: bool = False) -> ProviderConfig:
        if provider is Provider.OKTA:
            return OktaProviderConfig.configure(mfa_enabled)
        elif provider is Provider.GOOGLE:
            return GoogleProviderConfig.configure(mfa_enabled)
        elif provider is Provider.BASTION:
            return BastionProviderConfig.configure(mfa_enabled)


@dataclass
class BastionProviderConfig(ProviderConfig):
    profile_name: str

    @staticmethod
    def configure(mfa_enabled: bool = False) -> "BastionProviderConfig":
        config, c = ConfigManager(CONFIG_OVERRIDE_FILE_PATH), Utils.default_colors()

        profile = config.get_property(Config.Section.Bastion.PROFILE)
        if profile:
            print(f"\n\n{c.fg_bl}Default AWS Provider found in: {CONFIG_OVERRIDE_FILE_PATH}.{c.rs}")
            print(f"Value found: {profile}\n")
        else:
            profile = input('Please input your aws profile linked to your credentials in your `bastion` account: ')
            Utils.stc_validate(profile != '', "You must input a valid profile name.")

        return BastionProviderConfig(profile_name=profile)

    @property
    def profile(self):
        return self.profile_name


@dataclass
class GoogleProviderConfig(ProviderConfig):
    """
        idp_id: str -> Google's assigned IDP Identifier for your google authentication.
                       This can be found in your IDP metadata.xml file (or elsewhere, probably)
        sp_id: str ->  Service Provider ID: from your configured SAML app.
    """
    idp_id: str
    sp_id: str

    @staticmethod
    def configure(mfa_enabled: bool = False) -> "GoogleProviderConfig":
        config, c = ConfigManager(CONFIG_OVERRIDE_FILE_PATH), Utils.default_colors()
        idp_id = config.get_property(Config.Section.Google.IDP_ID)
        if idp_id:
            print(f"\n\n{c.fg_bl}Identity Provider Id found in: {CONFIG_OVERRIDE_FILE_PATH}.{c.rs}")
            print(f"Value found: {idp_id}\n")
        else:
            idp_id = input('Please input the Identity Provider ID associated with your Google Account: ')
            Utils.stc_is_valid_input(idp_id, "Identity Provider Id", True)

        sp_id = config.get_property(Config.Section.Google.SP_ID)
        if sp_id:
            print(f"\n\n{c.fg_bl}Service Provider Id found in: {CONFIG_OVERRIDE_FILE_PATH}.{c.rs}")
            print(f"Value found: {sp_id}\n")
        else:
            sp_id = input(
                'Please input the Service Provider ID associated with your Google SAML configuration (this is a '
                'number lke 123456789) : ')
            Utils.stc_is_valid_input(idp_id, "Service Provider Id", True)

        return GoogleProviderConfig(idp_id=idp_id, sp_id=sp_id)


@dataclass
class OktaProviderConfig(ProviderConfig):
    """
        app_link: str Application embed link for the company's AWS application in OKTA
                  Looks something like this: https://your-company.okta.com/home/amazon_aws/ASDF12351fg1/234'
    """
    app_link: str
    factor_type: str

    @property
    def base_url(self) -> str:
        result = re.match(r'^.*https://(.*\.com)/.*', self.app_link)
        if result:
            return result.group(1)
        else:
            Utils.stc_error_exit(f"Unable to parse base url from OKTA application link: {self.app_link}, are you "
                                 f"sure this link is valid?")

    @staticmethod
    def get_embed_link() -> str:
        app_link = input("Please input your OKTA AWS Application Embed Link. It's usually something like "
                         "'https://your-company.okta.com/home/amazon_aws/ASDF12351fg1/234': ")
        Utils.stc_is_valid_input(app_link, "OKTA AWS Application URL", True)
        return app_link

    @staticmethod
    def get_factor_type() -> str:
        factor_type = prompt(f"Please select your OKTA MFA Factor type. Supported Types are "
                             f"{SUPPORTED_OKTA_FACTOR_TYPES}: ",
                             completer=WordCompleter(SUPPORTED_OKTA_FACTOR_TYPES))
        Utils.stc_validate(OktaProviderConfig.factor_type in SUPPORTED_OKTA_FACTOR_TYPES,
                           f"You must select a factor type from: {SUPPORTED_OKTA_FACTOR_TYPES}")
        return factor_type

    @staticmethod
    def configure(mfa_enabled: bool = False) -> "OktaProviderConfig":
        config, c = ConfigManager(CONFIG_OVERRIDE_FILE_PATH), Utils.default_colors()
        app_link = config.get_or_prompt(Config.Section.Okta.APP_LINK, OktaProviderConfig.get_embed_link)

        if mfa_enabled:
            factor_type = config.get_or_prompt(Config.Section.Okta.FACTOR_TYPE, OktaProviderConfig.get_factor_type)
        else:
            factor_type = None

        return OktaProviderConfig(app_link=app_link, factor_type=factor_type)
