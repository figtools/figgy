import logging
from typing import Set

from data.dao.config import ConfigDao
from models.run_env import RunEnv
from svcs.cache_manager import CacheManager
from utils.utils import Utils

log = logging.getLogger(__name__)


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
            all_parameters = self._config_dao.get_all_config_names()
            self._cache_mgr.write(cache_key, all_parameters)
        else:

            # Get items from cache
            last_write, cached_contents = self._cache_mgr.get(cache_key)

            # Find new items added to remote cache table since last local cache write
            new_names = self._config_dao.get_config_names_after(last_write)

            # Add new names to cache
            self._cache_mgr.append(cache_key, new_names)

            all_parameters = set(cached_contents) | new_names

        return all_parameters
