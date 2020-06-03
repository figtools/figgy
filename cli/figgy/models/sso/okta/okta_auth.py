from abc import ABC, abstractmethod
from figgy.models.defaults.defaults import CLIDefaults
from figgy.models.sso.okta.okta_session import OktaSession


class OktaAuth(ABC):

    def __init__(self, defaults: CLIDefaults):
        self._defaults = defaults

    @property
    def app_link(self):
        return self._defaults.provider_config.app_link

    @property
    def base_url(self):
        return self._defaults.provider_config.base_url

    def factor_type(self):
        return self._defaults.provider_config.factor_type

    @abstractmethod
    def get_session(self) -> OktaSession:
        pass
