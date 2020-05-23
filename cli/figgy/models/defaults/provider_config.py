from abc import ABC, abstractmethod
from dataclasses import dataclass

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

from config import SUPPORTED_OKTA_FACTOR_TYPES
from input.input import Input, List
from utils.utils import Utils

from models.defaults.provider import Provider


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
        profile = input('Please input your aws profile linked to your credentials in your `bastion` account: ')
        Utils.stc_validate(profile != '', "You must input a valid profile name.")

        return BastionProviderConfig(profile_name=profile)


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
        idp_id = input('Please input the Identity Provider ID associated with your Google Account: ')
        Utils.stc_is_valid_input(idp_id, "Identity Provider Id", True)
        sp_id = input('Please input the Service Provider ID associated with your Google SAML configuration (this is a '
                      'number lke 123456789) : ')
        Utils.stc_is_valid_input(idp_id, "Service Provider Id", True)

        return GoogleProviderConfig(idp_id=idp_id, sp_id=sp_id)


@dataclass
class OktaProviderConfig(ProviderConfig):
    """

    """
    app_link: str
    base_url: str
    factor_type: str

    @staticmethod
    def configure(mfa_enabled: bool = False) -> "ProviderConfig":
        base_url = input("Please input the your OKTA domain. It's usually something like 'your-company.okta.com': ")
        Utils.stc_is_valid_input(base_url, "OKTA Domain", True)
        app_link = input("Please input your OKTA AWS Application Embed Link. It's usually something like "
                         "'https://your-company.okta.com/home/amazon_aws/ASDF12351fg1/234': ")
        Utils.stc_is_valid_input(app_link, "OKTA AWS Application URL", True)

        factor_type = None
        if mfa_enabled:
            factor_type = prompt(f"Please select your OKTA MFA Factor type. Supported Types are "
                                 f"{SUPPORTED_OKTA_FACTOR_TYPES}: ", completer=WordCompleter(SUPPORTED_OKTA_FACTOR_TYPES))
            Utils.stc_validate(factor_type in SUPPORTED_OKTA_FACTOR_TYPES,
                               f"You must select a factor type from: {SUPPORTED_OKTA_FACTOR_TYPES}")

        return OktaProviderConfig(app_link=app_link, base_url=base_url, factor_type=factor_type)
