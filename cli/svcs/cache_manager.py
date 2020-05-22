import logging
import json
import os
import jsonpickle
from typing import Dict, Any, Union, Set, Tuple, List, Callable, FrozenSet
from config import *
from utils.utils import Utils

log = logging.getLogger(__name__)


def write_empty_cache_file(path: str):
    with open(path, "w") as cache:
        cache.write(jsonpickle.dumps({}))
    log.info(f"Cache written at path: {path}")


def prime_cache(function):
    def inner(self, *args, **kwargs):
        if not os.path.exists(self._cache_file):
            log.info("Cache file doesn't exist. Priming cache file.")
            write_empty_cache_file(self._cache_file)
            log.info("Cache primed.")
        return function(self, *args, **kwargs)

    return inner


def wipe_bad_cache(function):
    def inner(self, *args, **kwargs):
        try:
            function(self, *args, **kwargs)
        except json.JSONDecodeError as e:
            log.info("Cache file has been corrupted, recreating.")
            os.remove(self._cache_file)
            write_empty_cache_file(self._cache_file)

        return function(self, *args, **kwargs)

    return inner


class CacheManager:
    """
    Manages a local cache file to enhance figgy performance
    """

    _STORE_KEY = 'cache'
    _LAST_WRITE_KEY = 'last_write'
    _LAST_REFRESH_KEY = 'last_refresh'
    DEFAULT_REFRESH_INTERVAL = 60 * 60 * 24 * 7 * 1000  # 1 week in MS

    def __init__(self, cache_name: Union[str, FrozenSet, None] = "default", file_override: Union[str, None] = None):
        cache_name = Utils.get_first(cache_name) if isinstance(cache_name, frozenset) else cache_name
        self._cache_file: str = f'{CACHE_OTHER_DIR}/{cache_name}-cache.json' if not file_override else file_override
        os.makedirs(CACHE_OTHER_DIR, exist_ok=True)
        if file_override:
            os.makedirs("/".join(file_override.split('/')[:-1]), exist_ok=True)

    def get_val_or_refresh(self, cache_key: str, refresher: Callable, *args, max_age=DEFAULT_REFRESH_INTERVAL) -> Any:
        last_write, val = self.get_or_refresh(cache_key, refresher, *args, max_age=max_age)
        return val

    @prime_cache
    @wipe_bad_cache
    def get_or_refresh(self, cache_key: str, refresher: Callable, *args, max_age=DEFAULT_REFRESH_INTERVAL) \
            -> Tuple[int, Any]:
        last_write, val = self.get(cache_key)
        if Utils.millis_since_epoch() - last_write > max_age or not val:
            new_val = refresher(*args)
            self.write(cache_key, new_val)
            return Utils.millis_since_epoch(), new_val
        else:
            return last_write, val

    @prime_cache
    @wipe_bad_cache
    def last_refresh(self, cache_key: str) -> int:
        """
        Return the last time the cache at this key was totally overwritten (and not just appended to)
        :param cache_key: key
        :return: int - millis since epoch - the last time this cache key was totally overwritten by the write method.
        """

        with open(self._cache_file, "r") as cache:
            cache_string = cache.read()
            contents: Dict = jsonpickle.decode(cache_string)

        return contents.get(cache_key, {}).get(self._LAST_REFRESH_KEY, 0)

    @prime_cache
    @wipe_bad_cache
    def write(self, cache_key: str, object: Any) -> None:
        """
        Write an object to a local cache file. This will overwrite any existing values.
        :param cache_key: str - The key to write your object to local cache under. You will use this to lookup from
                the cache later.
        :param object: Any - Object to write, must be serializable by `json` library
        """
        try:
            object = list(object) if isinstance(object, Set) else object  # set is not json serializable

            with open(self._cache_file, "r") as cache:
                contents: Dict = jsonpickle.decode(cache.read())

            with open(self._cache_file, "w+") as cache:
                contents[cache_key] = {
                    self._STORE_KEY: object,
                    self._LAST_WRITE_KEY: Utils.millis_since_epoch(),
                    self._LAST_REFRESH_KEY: Utils.millis_since_epoch()
                }

                cache.write(jsonpickle.dumps(contents))
        except Exception as e:
            print(f"Error writing to cache key: {cache_key}: {e}")

    @prime_cache
    @wipe_bad_cache
    def get(self, cache_key: str, default=None) -> Tuple[int, Any]:
        """
        Retrieve an item from the cache.
        :param cache_key: Key to return from the cache.
        :param default: Default value to return if the key doesn't exist in cache.
        :return: Tuple with last_write time, and the stored object.
        """

        with open(self._cache_file, "r") as cache:
            cache_contents = cache.read()
            contents: Dict = jsonpickle.decode(cache_contents)
            cache = contents.get(cache_key, {})
            result = cache.get(self._LAST_WRITE_KEY, 0), cache.get(self._STORE_KEY, default)
            log.info(f'Returning items from cache for cache key: {cache_key}')

        return result

    def get_val(self, cache_key: str, default=None) -> Any:
        return self.get(cache_key, default)[1]

    @prime_cache
    @wipe_bad_cache
    def append(self, cache_key: str, objects: Union[Dict, Set[Any]]):
        """
        Add a set or dictionary of items to the existing cache. Must be the SAME type as what is stored in the
        existing cache under cache_key.

        Lists not supported due to issues with duplicates continually growing in the local cache :)

        :param cache_key: Key to append or merge items with
        :param objects: Objects to add.
        """

        if isinstance(objects, Set):
            objects = list(objects)

        if len(objects) > 0:
            log.info(f'Appending {len(objects)} items to local cache: {objects}')

            with open(self._cache_file, "r") as cache:
                contents: Dict = jsonpickle.decode(cache.read())
                cache = contents.get(cache_key, {})
                refresh_time = cache.get(self._LAST_REFRESH_KEY, 0)
                cache_obj = cache.get(self._STORE_KEY)

                if isinstance(cache_obj, Dict) and isinstance(objects, Dict) or cache_obj is None:
                    if cache_obj:
                        cache_obj.update(objects)
                    else:
                        cache_obj = objects
                elif isinstance(cache_obj, List) and isinstance(objects, List) or cache_obj is None:
                    cache_obj = list(set(cache_obj + objects)) if cache_obj else objects
                else:
                    raise RuntimeError(
                        "Invalid state detected. Cache contains an invalid type that cannot be appended to, "
                        "or the type provided does not match the type stored in the cache.")

                contents[cache_key] = {
                    self._STORE_KEY: cache_obj,
                    self._LAST_WRITE_KEY: Utils.millis_since_epoch(),
                    self._LAST_REFRESH_KEY: refresh_time,
                }

            with open(self._cache_file, 'w') as cache:
                cache.write(jsonpickle.dumps(contents))
        else:
            log.info('No cached items found to add to cache.')

    def delete(self, cache_key: str, objects: Union[Dict, Set[Any]]):
        """
        If any of these items exist in the cache for this set of stored values, delete them.
        :param cache_key: Key to potentially delete items from
        :param objects: *Keys* in the cached DICT to delete, or items in a cached LIST to delete.
        """

        if isinstance(objects, Set):
            objects = list(objects)

        if len(objects) > 0:
            log.info(f'Deleting {len(objects)} items from local cache: {objects}')

            with open(self._cache_file, "r") as cache:
                contents: Dict = jsonpickle.decode(cache.read())
                cache = contents.get(cache_key, {})
                refresh_time = cache.get(self._LAST_REFRESH_KEY, 0)
                cache_obj = cache.get(self._STORE_KEY)
                log.info(f'In cache: {cache_obj}')

                if isinstance(cache_obj, Dict) and isinstance(objects, Dict) or cache_obj is None:
                    log.info(f'Cache Obj is a dict')
                    if cache_obj:
                        for obj in objects:
                            del cache_obj[obj]

                elif isinstance(cache_obj, List) and isinstance(objects, List) or cache_obj is None:
                    log.info(f"Cache obj is a list..")
                    if cache_obj:
                        cache_obj = list(set(cache_obj) - set(objects))

                else:
                    raise RuntimeError(
                        "Invalid state detected. Cache contains an invalid type that cannot be appended to, "
                        "or the type provided does not match the type stored in the cache.")

                log.info(f'New cache obj: {cache_obj}')
                contents[cache_key] = {
                    self._STORE_KEY: cache_obj,
                    self._LAST_WRITE_KEY: Utils.millis_since_epoch(),
                    self._LAST_REFRESH_KEY: refresh_time,
                }

            with open(self._cache_file, 'w') as cache:
                cache.write(jsonpickle.dumps(contents))
        else:
            log.info('No cached items found to add to cache.')

    def wipe_cache(self):
        with open(self._cache_file, "w") as cache:
            cache.write(jsonpickle.dumps({}))
