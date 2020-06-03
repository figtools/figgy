import json
import logging
import os

import boto3

from botocore.errorfactory import ClientError
from botocore.exceptions import NoCredentialsError, ParamValidationError
from json import JSONDecodeError
from figgy.config import *
from figgy.models.assumable_role import AssumableRole
from figgy.models.defaults.defaults import CLIDefaults
from figgy.svcs.sso.okta.okta import Okta
from figgy.svcs.sso.provider.session_provider import SessionProvider
from figgy.utils.utils import Utils, InvalidSessionError

log = logging.getLogger(__name__)


class SessionManager:
    _MAX_ATTEMPTS = 5

    def __init__(self, colors_enabled: bool, defaults: CLIDefaults, session_provider: SessionProvider):
        self._sts = boto3.client('sts')
        self._utils = Utils(colors_enabled)
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