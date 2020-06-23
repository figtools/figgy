import jsonpickle
import uuid
import os
from figcli.models.assumable_role import AssumableRole
from figcli.models.defaults.provider import Provider
from figcli.models.defaults.provider_config import ProviderConfig, ProviderConfigFactory, BastionProviderConfig
from figcli.models.role import Role
from figcli.models.run_env import RunEnv
from figcli.config.constants import APP_NS_OVERRIDE
from figcli.config import *
from typing import Dict, Optional, List, Any
from dataclasses import dataclass, field
from figcli.utils.utils import Utils


@dataclass
class CLIDefaults:
    """
    Defaults are parsed from the ~/.figgy/devops/defaults file and then hydrate this object
    """
    user_id: Optional[str]
    role: Optional[Role]
    colors_enabled: bool
    run_env: RunEnv
    region: str
    mfa_enabled: bool
    service_ns: str
    provider: Provider
    session_duration: int
    usage_tracking: bool
    report_errors: Optional[bool]
    auto_mfa: Optional[bool]
    provider_config: Optional[Any]
    mfa_serial: Optional[str]
    user: Optional[str]
    valid_envs: Optional[List[RunEnv]] = field(default_factory=list)
    valid_roles: Optional[List[Role]] = field(default_factory=list)
    assumable_roles: Optional[List[AssumableRole]] = field(default_factory=list)
    extras: Optional[Dict] = field(default_factory=dict)

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
                           session_duration=DEFAULT_SESSION_DURATION,
                           region="us-east-1",
                           mfa_enabled=False,
                           mfa_serial=None,
                           provider_config=None,
                           report_errors=False,
                           auto_mfa=False,
                           user_id=str(uuid.uuid4()),
                           service_ns="/app",
                           usage_tracking=False,
                           extras={})

    @staticmethod
    def sandbox(user: str, role: str, colors: bool):
        return CLIDefaults(role=Role(role),
                           colors_enabled=colors,
                           user=user,
                           run_env=RunEnv("unconfigured"),
                           provider=Provider.AWS_BASTION,
                           session_duration=SANDBOX_SESSION_DURATION,
                           region=FIGGY_SANDBOX_REGION,
                           mfa_enabled=False,
                           mfa_serial=None,
                           provider_config=BastionProviderConfig(FIGGY_SANDBOX_PROFILE),
                           report_errors=False,
                           auto_mfa=False,
                           user_id=str(uuid.uuid4()),
                           service_ns="/app",
                           usage_tracking=True,
                           extras={DISABLE_KEYRING: True})

    @staticmethod
    def from_profile(profile):
        return CLIDefaults(role=Role(profile),
                           colors_enabled=Utils.not_windows(),
                           user=profile,
                           run_env=RunEnv(profile),
                           provider=Provider.PROFILE,
                           session_duration=DEFAULT_SESSION_DURATION,
                           region="us-east-1",
                           mfa_enabled=False,
                           mfa_serial=None,
                           provider_config=None,
                           report_errors=False,
                           auto_mfa=False,
                           user_id=str(uuid.uuid4()),
                           service_ns=os.environ.get(APP_NS_OVERRIDE) or "/app",
                           usage_tracking=True,
                           extras={})

    def __str__(self) -> str:
        return jsonpickle.encode(self)
