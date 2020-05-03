from dataclasses import dataclass
from typing import List

from models.role import Role
from models.run_env import RunEnv
from tabulate import tabulate


@dataclass
class AssumableRole:
    account_id: int
    role: Role
    run_env: RunEnv

    def tabulate_data(self) -> List[str]:
        return [self.account_id, self.run_env.env, self.role.role]

    def tabulate_header(self):
        return ["Account #", "Environment", "Role"]

    def print(self):
        print(self.__dict__)

    def __str__(self):
        return tabulate(
                [self.tabulate_data()],
                headers=self.tabulate_header(),
                tablefmt="grid",
                numalign="center",
                stralign="left",
            )