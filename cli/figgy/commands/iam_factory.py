from figgy.commands.factory import Factory
from figgy.commands.iam.export import Export
from figgy.commands.iam_context import IAMContext
from figgy.utils.utils import *
from figgy.config import *
from boto3.session import Session
from typing import Optional


class IAMFactory(Factory):
    def __init__(self, command: frozenset, context: IAMContext, env_session: Session,
                 all_sessions: Optional[Dict[str, Session]] = None):

        self._all_sessions: Optional[Dict[str, Session]] = all_sessions
        self._command = command
        self._utils = Utils(context.colors_enabled)
        self._iam_context: IAMContext = context
        self._env_session: Session = env_session

    def instance(self):
        return self.get(self._command)

    def get(self, command: frozenset):
        if command == export:
            return Export(self._iam_context, self._env_session, self._all_sessions)
        else:
            self._utils.error_exit(f"{command} is not a valid IAM command. You must select from: "
                                   f"[{CollectionUtils.printable_set(iam_commands)}]. Try using --help for more info.")
