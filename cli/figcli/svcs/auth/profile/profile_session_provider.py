from typing import List
import boto3
import botocore

from figcli.models.assumable_role import AssumableRole
from figcli.models.defaults.defaults import CLIDefaults
from figcli.svcs.auth.provider.session_provider import SessionProvider
from figcli.utils.utils import Utils

class ProfileSessionProvider(SessionProvider):
    """
    This provider is not recommended; however, I recognize it is useful for 2 main use cases.

    1) Companies with a single AWS account.
    2) Automating CICD pipelines.

    This provider always returns a session from the targeted profile.
    """

    def __init__(self, defaults: CLIDefaults):
        super().__init__(defaults)

    def get_session(self, assumable_role: AssumableRole, prompt: bool, exit_on_fail=True) -> boto3.Session:

        try:
            return boto3.Session(profile_name=assumable_role.profile)
        except botocore.exceptions.ProfileNotFound:
            Utils.stc_error_exit(f"The provided profile override of {assumable_role.profile} is invalid. Are you sure "
                                 f"this profile is set in your ~/.aws/credentials and ~/.aws/config files?")

    def cleanup_session_cache(self):
        pass
