from config import *


class Account:

    def __init__(self, account: str):
        assert account in account_types, f"Provided account must be one of: {account_types}"
        self.account = account

    def __str__(self):
        return self.account

    def __eq__(self, other):
        return self.account == other.account
