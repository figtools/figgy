import json
import logging
import os

import boto3

from botocore.errorfactory import ClientError
from botocore.exceptions import NoCredentialsError, ParamValidationError
from json import JSONDecodeError
from figcli.config import *
from figcli.models.assumable_role import AssumableRole
from figcli.models.defaults.defaults import CLIDefaults
from figcli.svcs.auth.okta.okta import Okta
from figcli.svcs.auth.provider.session_provider import SessionProvider
from figcli.utils.utils import Utils, InvalidSessionError

log = logging.getLogger(__name__)


class SessionManager:
    _MAX_ATTEMPTS = 5

    def __init__(self, defaults: CLIDefaults, session_provider: SessionProvider):
        self._sts = boto3.client('sts')
        self._utils = Utils(defaults.colors_enabled)
        self._defaults = defaults
        self.session_provider: SessionProvider = session_provider

    @Utils.trace
    def get_session(self, assumable_role: AssumableRole, prompt: bool, exit_on_fail=True) -> boto3.Session:
        """
        Creates a session in the specified ENV for the target role from a SAML assertion returned by OKTA authentication.
        Args:
            assumable_role: AssumableRole - The role to be leveraged to authenticate this session
            prompt: If prompt is set, we will not use a cached session and will generate new sessions for okta and mgmt.
            exit_on_fail: Exit the program if this session hydration fails.

        returns: Hydrated session for role + account that match the specified one in the provided AssumableRole
        """
        return self.session_provider.get_session(assumable_role, prompt, exit_on_fail=exit_on_fail)