from figcli.models.sso.okta.okta_auth import OktaAuth
from figcli.models.sso.okta.okta_session import OktaSession


class OktaSessionAuth(OktaAuth):
    def __init__(self, session: OktaSession):
        self.session = session

    def get_session(self):
        return self.session
