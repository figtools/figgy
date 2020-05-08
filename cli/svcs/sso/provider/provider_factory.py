from commands.factory import Factory
from models.defaults.defaults import CLIDefaults
from models.defaults.provider import Provider
from svcs.sso.okta.okta_session_provider import OktaSessionProvider
from svcs.sso.provider.session_provider import SessionProvider


class SessionProviderFactory(Factory):

    def __init__(self, defaults: CLIDefaults):
        self._defaults = defaults

    def instance(self) -> SessionProvider:
        if self._defaults.provider is Provider.OKTA:
            return OktaSessionProvider(self._defaults)
        else:
            raise NotImplementedError(f"Provider: {self._defaults.provider} is not currently supported.")
