import json
import logging
from typing import List

from prompt_toolkit.completion import WordCompleter

from figcli.config import *
from figcli.data.dao.ssm import SsmDao
from figcli.models.role import Role
from figcli.models.run_env import RunEnv
from figcli.svcs.cache_manager import CacheManager
from figcli.svcs.config import ConfigService
from figcli.utils.utils import Utils

log = logging.getLogger(__name__)

class RBACLimitedConfigView:
    """
    Returns limited sets of configuration names based on the user's role's access
    """

    def __init__(self, role: Role, cache_mgr: CacheManager, ssm: SsmDao, config_svc: ConfigService):
        self._role = role
        self._cache_mgr = cache_mgr
        self._config_svc = config_svc
        self._ssm = ssm
        self.rbac_role_ns_path = f'{figgy_ns}/rbac/{self._role.role}/namespaces'
        self.rbac_role_kms_path = f'{figgy_ns}/rbac/{self._role.role}/keys'
        self._config_completer = None

    def get_authorized_namespaces(self) -> List[str]:
        """
        Looks up the user-defined namespaces that users of this type can access. This enables us to prevent the
        auto-complete from showing parameters the user doesn't actually have access to.

        If the user's defined accessible namespaces are not available, then returns all root namespaces, regardless
        of whether use is authorized to perform GET requests against those values.

        Leverages an expiring local cache to save ~200ms on each figgy bootstrap
        """
        cache_key = f'{self._role.role}-authed-nses'

        es, authed_nses = self._cache_mgr.get_or_refresh(cache_key, self._ssm.get_parameter, self.rbac_role_ns_path)

        if authed_nses:
            if isinstance(authed_nses, str):
                authed_nses = json.loads(authed_nses)
        else:
            es, authed_nses = self._cache_mgr.get_or_refresh(cache_key, self._config_svc.get_root_namespaces)

        if not isinstance(authed_nses, list):
            raise ValueError(f"Invalid value found at path: {self.rbac_role_ns_path}. It must be a valid json List[str]")

        return authed_nses

    def get_authorized_kms_keys(self) -> List[str]:
        """
        Looks up the user-defined KMS keys that users of this type can access. This enables us to prevent the
        auto-complete from showing keys the user doesn't actually have access to.

        Leverages an expiring local cache to save ~200ms on each figgy bootstrap
        """
        cache_key = f'{self._role.role}-authed-keys'

        es, authed_nses = self._cache_mgr.get_or_refresh(cache_key, self._ssm.get_parameter, self.rbac_role_kms_path)

        if authed_nses:
            authed_nses = json.loads(authed_nses)

        if not isinstance(authed_nses, list):
            raise ValueError(f"Invalid value found at path: {self.rbac_role_kms_path}. It must be a valid json List[str]")

        return authed_nses

    def get_authorized_key_id(self, authorized_key_name: str, run_env: RunEnv) -> str:
        """
        Returns the appropriate KMS Key ID for a provided authorized key name.
        :param authorized_key_name: KMS Key the provider user has access to.
        :param run_env: Run environment associated with this key
        :return: KMS Key id of the associated key.
        """
        cache_key = f'kms-{authorized_key_name}-{run_env.env}'
        key_path = f'/figgy/kms/{authorized_key_name}-key-id'

        if authorized_key_name not in self.get_authorized_kms_keys():
            raise ValueError(f"You do not have access to encrypt with the KMS key: {authorized_key_name}")

        es, key_id = self._cache_mgr.get_or_refresh(cache_key, self._ssm.get_parameter, key_path)
        return key_id

    @Utils.trace
    def get_config_names(self, prefix: str = None, one_level: bool = False) -> List[str]:
        all_names = sorted(self._config_svc.get_parameter_names())
        authed_nses = self.get_authorized_namespaces()
        new_names = [] if authed_nses or prefix else all_names

        if prefix:
            is_child = False
            for ns in authed_nses:
                if prefix.startswith(ns):
                    is_child = True

            if not is_child and authed_nses:
                raise ValueError(f"Provided prefix of {prefix} is not in a valid authorized namespace.")

            authed_nses = [prefix]

        for ns in authed_nses:
            filtered_names = [name for name in all_names if name.startswith(ns)]
            new_names = new_names + filtered_names

        if one_level:
            if prefix:
                new_names = [name for name in new_names if len(name.split('/')) == len(prefix.split('/')) + 1]
            else:
                new_names = authed_nses

        return new_names

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
            self._config_completer = WordCompleter(self.get_config_names(), sentence=True, match_middle=True)

        # print(f"Cache Count: {len(all_names)}")
        return self._config_completer
