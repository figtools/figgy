from figcli.config import *


class Account:

    def __init__(self, account: str):
        self.account = account

    def __str__(self):
        return self.account

    def __eq__(self, other):
        return self.account == other.account
