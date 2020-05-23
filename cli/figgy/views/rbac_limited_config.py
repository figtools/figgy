import json
from typing import List

from prompt_toolkit.completion import WordCompleter

from config import *
from data.dao.ssm import SsmDao
from models.role import Role
from svcs.cache_manager import CacheManager
from svcs.config import ConfigService
from utils.utils import Utils


class RBACLimitedConfigView:
    """
    Returns limited sets of configuration names based on the user's role's access
    """

    def __init__(self, role: Role, cache_mgr: CacheManager, ssm: SsmDao, config_svc: ConfigService):
        self._role = role
        self._cache_mgr = cache_mgr
        self._config_svc = config_svc
        self._ssm = ssm
        self.rbac_role_path = f'{figgy_ns}/rbac/{self._role.role}'
        self._config_completer = None

    def get_authed_namespaces(self) -> List[str]:
        """
        Looks up the user-defined namespaces that users of this type can access. This enables us to prevent the
        auto-complete from showing parameters the user doesn't actually have access to.

        Leverages an expiring local cache to save ~200ms on each figgy bootstrap
        """
        cache_key = f'{self._role.role}-authed-nses'

        es, authed_nses = self._cache_mgr.get_or_refresh(cache_key, self._ssm.get_parameter, self.rbac_role_path)

        if authed_nses:
            authed_nses = json.loads(authed_nses)

        if not isinstance(authed_nses, list):
            raise ValueError(f"Invalid value found at path: {self.rbac_role_path}. It must be a valid json List[str]")

        return authed_nses

    def get_authorized_namespaces(self):
        return self._ssm.get_parameter(self.rbac_role_path)

    @Utils.trace
    def get_config_completer(self):
        """
        This is used to be a slow operation since it involves pulling all parameter names from Parameter Store.
        It's best to be lazy loaded only if the dependent command requires it. It's still best to be lazy loaded,
        but it is much faster now that we have implemented caching of existing parameter names in DynamoDb and
        locally.
        """
        # Not the most efficient, but plenty fast since we know the # of authed_nses is gonna be ~<=5
        # Tested at 30k params and it takes ~25ms
        if not self._config_completer:
            all_names = sorted(self._config_svc.get_parameter_names())
            authed_nses = self.get_authed_namespaces() + [shared_ns]
            new_names = []
            for ns in authed_nses:
                filtered_names = [name for name in all_names if name.startswith(ns)]
                new_names = new_names + filtered_names

            self._config_completer = WordCompleter(new_names, sentence=True, match_middle=True)

        # print(f"Cache Count: {len(all_names)}")
        return self._config_completer
