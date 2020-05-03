from config import *
from abc import ABC, abstractmethod
from utils.utils import *
import logging
from models.sso.okta.okta_auth import OktaAuth


class OktaConfig:

    def __init__(self, okta_auth: OktaAuth):
        self.base_url = OKTA_BASE_URL
        self.app_link = OKTA_APP_LINK
        self.duration = OKTA_SESSION_DURATION
        self.okta_auth = okta_auth



