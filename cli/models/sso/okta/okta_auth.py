from abc import ABC, abstractmethod

from models.sso.okta.okta_session import OktaSession


class OktaAuth(ABC):
    @abstractmethod
    def get_session(self) -> OktaSession:
        pass
