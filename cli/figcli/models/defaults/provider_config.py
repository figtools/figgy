from abc import ABC, abstractmethod
from dataclasses import dataclass

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

from figcli.config import Config, CONFIG_OVERRIDE_FILE_PATH, SUPPORTED_OKTA_FACTOR_TYPES, FAKE_GOOGLE_IDP_ID, FAKE_GOOGLE_SP_ID, FAKE_OKTA_APP_LINK
from figcli.input.input import Input, List
from figcli.svcs.config_manager import ConfigManager
from figcli.utils.utils import Utils, Color
from figcli.config.communication import *

from figcli.models.defaults.provider import Provider
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
        elif provider is Provider.AWS_BASTION:
            return BastionProviderConfig.configure(mfa_enabled)


@dataclass
class BastionProviderConfig(ProviderConfig):
    profile_name: str

    @staticmethod
    def get_profile():
        profile = input('Please input your aws profile linked to your credentials in your `bastion` account: ')
        Utils.stc_validate(profile != '', "You must input a valid profile name.")
        return profile

    @staticmethod
    def configure(mfa_enabled: bool = False) -> "BastionProviderConfig":
        config, c = ConfigManager(CONFIG_OVERRIDE_FILE_PATH), Utils.default_colors()
        profile = config.get_or_prompt(Config.Section.Bastion.PROFILE, BastionProviderConfig.get_profile)
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
    def get_idp_id():
        idp_id = input('\nPlease input the Identity Provider ID associated with your Google Account: ')
        Utils.stc_is_valid_input(idp_id, "Identity Provider Id", True)
        return idp_id

    @staticmethod
    def get_sp_id():
        sp_id = input('\nPlease input the Service Provider ID associated with your Google SAML configuration (this is a '
            'number lke 123456789) : ')
        Utils.stc_is_valid_input(sp_id, "Service Provider Id", True)
        return sp_id

    @staticmethod
    def configure(mfa_enabled: bool = False) -> "GoogleProviderConfig":
        config, c = ConfigManager(CONFIG_OVERRIDE_FILE_PATH), Utils.default_colors()

        idp_id = config.get_property(Config.Section.Google.IDP_ID)
        sp_id = config.get_property(Config.Section.Google.SP_ID)

        if idp_id and idp_id != FAKE_GOOGLE_IDP_ID:
            idp_id = config.get_or_prompt(Config.Section.Google.IDP_ID, GoogleProviderConfig.get_idp_id)
        else:
            idp_id = config.get_or_prompt(Config.Section.Google.IDP_ID, GoogleProviderConfig.get_idp_id, force_prompt=True)

        if sp_id and sp_id != FAKE_GOOGLE_SP_ID:
            sp_id = config.get_or_prompt(Config.Section.Google.SP_ID, GoogleProviderConfig.get_sp_id)
        else:
            sp_id = config.get_or_prompt(Config.Section.Google.SP_ID, GoogleProviderConfig.get_sp_id, force_prompt=True)

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
    def get_app_link() -> str:
        app_link = Input.input("Please input your OKTA AWS Application Embed Link. It's usually something like "
                         "'https://your-company.okta.com/home/amazon_aws/ASDF12351fg1/234': ")
        Utils.stc_is_valid_input(app_link, "OKTA AWS Application URL", True)
        return app_link

    @staticmethod
    def get_factor_type() -> str:
        factor_type = prompt(f"\nPlease select your OKTA MFA Factor type. Supported Types are "
                             f"{SUPPORTED_OKTA_FACTOR_TYPES}: ",
                             completer=WordCompleter(SUPPORTED_OKTA_FACTOR_TYPES))
        Utils.stc_validate(factor_type in SUPPORTED_OKTA_FACTOR_TYPES,
                           f"You must select a factor type from: {SUPPORTED_OKTA_FACTOR_TYPES}")
        return factor_type

    @staticmethod
    def configure(mfa_enabled: bool = False) -> "OktaProviderConfig":
        config, c = ConfigManager(CONFIG_OVERRIDE_FILE_PATH), Utils.default_colors()
        app_link = config.get_property(Config.Section.Google.IDP_ID)
        if app_link and app_link != FAKE_OKTA_APP_LINK:
            app_link = config.get_or_prompt(Config.Section.Okta.APP_LINK, OktaProviderConfig.get_app_link,
                                            desc=OKTA_APP_LINK_DESC)
        else:
            app_link = config.get_or_prompt(Config.Section.Okta.APP_LINK, OktaProviderConfig.get_app_link,
                                            force_prompt=True, desc=OKTA_APP_LINK_DESC)

        if mfa_enabled:
            factor_type = config.get_or_prompt(Config.Section.Okta.FACTOR_TYPE, OktaProviderConfig.get_factor_type,
                                               desc=OKTA_MFA_TYPE_DESC)
        else:
            factor_type = None

        return OktaProviderConfig(app_link=app_link, factor_type=factor_type)
