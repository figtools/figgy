from config import *
from abc import ABC, abstractmethod
from utils.utils import *


class OktaSession:
    def __init__(self, session_token: str, session_id: str):
        self.session_token = session_token
        self.session_id = session_id


class OktaAuth(ABC):
    @abstractmethod
    def get_session(self) -> OktaSession:
        pass

