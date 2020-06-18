from collections import namedtuple
from typing import Optional

from boto3.session import Session

from figcli.commands.iam_context import IAMContext
from figcli.commands.types.iam import IAMCommand
from figcli.svcs.observability.anonymous_usage_tracker import AnonymousUsageTracker
from figcli.utils.utils import *
from figcli.utils.awscli import AWSCLIUtils


class Export(IAMCommand):
    """
    Returns audit history for a queried PS Name
    """

    def __init__(self, iam_context: IAMContext, env_session: Session,
                 all_sessions: Optional[Dict[str, Session]]):
        super().__init__(export, iam_context)
        self._all_sessions: Optional[Dict[str, Session]] = all_sessions
        self._env_session: Session = env_session

    def _export(self):
        if not self._all_sessions:
            credentials: namedtuple = self._env_session.get_credentials().get_frozen_credentials()
            Utils.stc_validate(credentials is not None,
                               f"Unable to generate credentials for environment: {self.run_env}")
            AWSCLIUtils.write_credentials(credentials.access_key, credentials.secret_key, credentials.token,
                                          region=self.context.defaults.region, color=self.c)
        else:
            for (role_name, session) in self._all_sessions.items():
                credentials: namedtuple = session.get_credentials().get_frozen_credentials()
                Utils.stc_validate(credentials is not None, f"Unable to generate credentials for role: {role_name}")
                AWSCLIUtils.write_credentials(credentials.access_key, credentials.secret_key, credentials.token,
                                              profile_name=role_name, region=self.context.defaults.region, color=self.c)

    @AnonymousUsageTracker.track_command_usage
    def execute(self):
        self._export()
