from dataclasses import dataclass
from typing import List, Optional

from figcli.models.defaults.provider import Provider
from figcli.models.role import Role
from figcli.models.run_env import RunEnv
from tabulate import tabulate


@dataclass
class AssumableRole:
    account_id: int
    run_env: RunEnv
    role: Optional[Role]
    provider_name: Optional[str]
    profile: Optional[str]

    def tabulate_data(self) -> List[str]:
        return [f'{self.account_id[0:5]} REDACTED', self.run_env.env, self.role.role]

    def tabulate_header(self):
        return ["Account #", "Environment", "Role"]

    def print(self):
        print(self.__dict__)

    @staticmethod
    def from_profile(profile: str):
        return AssumableRole(
            account_id=1234567899,
            run_env=RunEnv(env=profile),
            profile=profile,
            role=Role(profile),
            provider_name=Provider.PROFILE.value)

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
               self.run_env == other.run_env and \
               self.profile == other.profile

    def __hash__(self):
        return hash(f'{self.account_id}-{self.role}-{self.run_env}')