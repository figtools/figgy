import jsonpickle

from models.assumable_role import AssumableRole
from models.defaults.provider import Provider
from models.role import Role
from models.run_env import RunEnv
from config import *
from typing import Dict, Optional, List
from dataclasses import dataclass, field


@dataclass
class CLIDefaults:
    """
    Defaults are parsed from the ~/.figgy/devops/defaults file and then hydrate this object
    """
    role: Optional[Role]
    colors_enabled: bool
    run_env: RunEnv
    region: str
    mfa_enabled: bool
    provider: Provider
    mfa_serial: Optional[str]
    user: Optional[str]
    profile: Optional[str]
    valid_envs: Optional[List[RunEnv]] = field(default_factory=list)
    valid_roles: Optional[List[Role]] = field(default_factory=list)
    assumable_roles: Optional[List[AssumableRole]] = field(default_factory=list)

    def __str__(self):
        return f"Role: {self.role}\nColors Enabled: {self.colors_enabled}\nOkta User: {self.user}\n" \
               f"Default Environment: {self.run_env}"

    @staticmethod
    def unconfigured():
        return CLIDefaults(role=Role("unconfigured"),
                           colors_enabled=False,
                           user=None,
                           run_env=RunEnv("unconfigured"),
                           provider=Provider.UNSELECTED,
                           profile="unconfigured",
                           region="unconfigured",
                           mfa_enabled=False,
                           mfa_serial=None)

    @staticmethod
    def from_dict(config: Dict):
        role: Role = Role(config.get(DEFAULTS_ROLE_KEY))
        colors_enabled = config.get(DEFAULTS_COLORS_ENABLED_KEY)
        user_name = config.get(DEFAULTS_USER_KEY)
        region = config.get(DEFAULTS_REGION_KEY)
        env = RunEnv(config.get(DEFAULTS_ENV_KEY, "unconfigured"))  # Default to dev if missing.
        provider = Provider(config.get(DEFAULTS_PROVIDER_KEY), Provider.UNSELECTED)
        profile = config.get(DEFAULTS_PROFILE_KEY)

        return CLIDefaults(role=role, colors_enabled=colors_enabled, user=user_name,
                           run_env=env, provider=provider, profile=profile, region=region)

    def __str__(self) -> str:
        return jsonpickle.encode(self)
