from dataclasses import dataclass


@dataclass
class OktaSession:
    session_id: str
    session_token: str
