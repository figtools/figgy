from dataclasses import dataclass
from typing import List, Optional

from figgy.models.role import Role
from figgy.models.run_env import RunEnv
from tabulate import tabulate


@dataclass
class AssumableRole:
    account_id: int
    role: Role
    run_env: RunEnv
    provider_name: Optional[str]

    def tabulate_data(self) -> List[str]:
        return [self.account_id, self.run_env.env, self.role.role]

    def tabulate_header(self):
        return ["Account #", "Environment", "Role"]

    def print(self):
        print(self.__dict__)

    @property
    def role_arn(self) -> str:
        return f"arn:aws:iam::{self.account_id}:role/{self.role.full_name}"

    def __str__(self):
        return tabulate(
            [self.tabulate_data()],
            headers=self.tabulate_header(),
            tablefmt="grid",
            numalign="center",
            stralign="left",
        )

    def __eq__(self, other):
        return self.account_id == other.account_id and \
               self.role == other.role and \
               self.run_env == other.run_env

    def __hash__(self):
        return hash(f'{self.account_id}-{self.role}-{self.run_env}')