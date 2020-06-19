from enum import Enum
from typing import List


class Provider(Enum):
    OKTA = "okta"
    GOOGLE = "google"
    # MICROSOFT = "microsoft"
    # GENERIC_SAML = "saml"
    AWS_BASTION = "bastion"
    PROFILE = "profile"
    UNSELECTED = 0

    @staticmethod
    def sso_providers() -> List["Provider"]:
        return [Provider.OKTA, Provider.GOOGLE]

    @staticmethod
    def names():
        return [provider.name for provider in Provider]

    @staticmethod
    def values():
        return [provider.value for provider in Provider]

    @staticmethod
    def new(name: str):
        if name not in Provider.names():
            return Provider.UNSELECTED
        else:
            return Provider[name]
