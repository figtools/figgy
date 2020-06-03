from figgy.commands.factory import Factory
from figgy.models.defaults.defaults import CLIDefaults
from figgy.models.defaults.provider import Provider
from figgy.svcs.sso.google.google_session_provider import GoogleSessionProvider
from figgy.svcs.sso.bastion.bastion_session_provider import BastionSessionProvider
from figgy.svcs.sso.okta.okta_session_provider import OktaSessionProvider
from figgy.svcs.sso.provider.session_provider import SessionProvider


class SessionProviderFactory(Factory):

    def __init__(self, defaults: CLIDefaults):
        self._defaults = defaults
        self.__bastion_session_provider = None
        self.__okta_session_provider = None
        self.__google_session_provider = None

    def instance(self) -> SessionProvider:
        if self._defaults.provider is Provider.OKTA:
            if not self.__okta_session_provider:
                self.__okta_session_provider = OktaSessionProvider(self._defaults)

            return self.__okta_session_provider
        elif self._defaults.provider is Provider.AWS_BASTION:
            if not self.__bastion_session_provider:
                self.__bastion_session_provider = BastionSessionProvider(self._defaults)

            return self.__bastion_session_provider
        elif self._defaults.provider is Provider.GOOGLE:
            if not self.__google_session_provider:
                self.__google_session_provider = GoogleSessionProvider(self._defaults)

            return self.__google_session_provider
        else:
            raise NotImplementedError(f"Provider: {self._defaults.provider} is not currently supported.")
