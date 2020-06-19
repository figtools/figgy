import logging
from typing import Set, List

from figcli.data.dao.config import ConfigDao
from figcli.data.models.config_item import ConfigState, ConfigItem
from figcli.models.run_env import RunEnv
from figcli.svcs.cache_manager import CacheManager
from figcli.utils.utils import Utils

log = logging.getLogger(__name__)


# Todo, lots more from SSMDao should be moved here.
class ConfigService:
    __CACHE_REFRESH_INTERVAL = 60 * 60 * 24 * 7 * 1000  # 1 week in MS
    """
    Service level class for interactive with config resources.

    Currently contains some business logic to leverage a both local (filesystem) & remote (dynamodb)
    cache for the fastest possible lookup times.
    """
    _PS_NAME_CACHE_KEY = 'parameter_names'

    def __init__(self, config_dao: ConfigDao, cache_mgr: CacheManager, run_env: RunEnv):
        self._config_dao = config_dao
        self._cache_mgr = cache_mgr
        self._run_env = run_env

    def get_root_namespaces(self) -> List[str]:
        all_params = self.get_parameter_names()
        return sorted(list(set([f"/{p.split('/')[1]}" for p in all_params])))

    @Utils.trace
    def get_parameter_names(self) -> Set[str]:
        """
        Looks up local cached configs, then queries new config names from the remote cache, merges the two, and
        finally updates the local cache. This ensures very fast bootstrap times b/c querying thousands of parameter
        names from a remote cache can a bit too much time. `figgy` does not accept slow performance.

        :return: Set[str] names of all configs stored in ParameterStore.
        """
        cache_key = f'{self._run_env.env}-{self._PS_NAME_CACHE_KEY}'

        # Find last cache full refresh date
        last_refresh = self._cache_mgr.last_refresh(cache_key)

        # Do a full refresh if cache is too old.
        if Utils.millis_since_epoch() - last_refresh > self.__CACHE_REFRESH_INTERVAL:
            configs: Set[ConfigItem] = self._config_dao.get_config_names_after(0)
            all_parameters: Set[str] = set([x.name for x in configs if x.state == ConfigState.ACTIVE])
            self._cache_mgr.write(cache_key, all_parameters)
        else:

            # Get items from cache
            last_write, cached_contents = self._cache_mgr.get(cache_key)

            # Find new items added to remote cache table since last local cache write
            updated_items: Set[ConfigItem] = self._config_dao.get_config_names_after(last_write)

            # Add new names to cache
            added_names, deleted_names = set(), set()
            for item in updated_items:
                if item.state is ConfigState.ACTIVE:
                    log.info(f"ADDING NEW: {item}")
                    added_names.add(item.name)
                elif item.state is ConfigState.DELETED:
                    log.info(f"ADDING DELETED: {item}")
                    deleted_names.add(item.name)
                else:
                    # Default to add if no state set
                    added_names.add(item.name)

            self._cache_mgr.append(cache_key, added_names)
            self._cache_mgr.delete(cache_key, deleted_names)

            log.debug(f"Cached: {cached_contents}")
            log.debug(f"Cached: {deleted_names}")
            log.debug(f"Cached: {added_names}")

            all_parameters = set(cached_contents) - deleted_names | added_names

        return all_parameters
