from models.sso.okta.okta_auth import OktaAuth, OktaSession


class OktaSessionAuth(OktaAuth):
    def __init__(self, session_token: str, session_id: str):
        self._session_token = session_token
        self._session_id = session_id

    def get_session(self):
        return OktaSession(self._session_token, self._session_id)
