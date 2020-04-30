import logging
import json
import os
from typing import Dict, Any, Union, Set, Tuple, List
from config import *
from utils.utils import Utils

log = logging.getLogger(__name__)


def write_empty_cache_file(path: str):
    with open(path, "w") as cache:
        cache.write(json.dumps({}))
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

    def __init__(self, cache_name: str):
        self._cache_file: str = f'{CACHE_OTHER_DIR}/{cache_name}-cache.json'
        os.makedirs(CACHE_OTHER_DIR, exist_ok=True)

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
            contents: Dict = json.loads(cache_string)

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
        object = list(object) if isinstance(object, Set) else object  # set is not json serializable

        with open(self._cache_file, "r") as cache:
            contents: Dict = json.loads(cache.read())

        with open(self._cache_file, "w+") as cache:
            contents[cache_key] = {
                self._STORE_KEY: object,
                self._LAST_WRITE_KEY: Utils.millis_since_epoch(),
                self._LAST_REFRESH_KEY: Utils.millis_since_epoch()
            }

            cache.write(json.dumps(contents))

    @prime_cache
    @wipe_bad_cache
    def get(self, cache_key: str) -> Tuple[int, Union[Dict, List]]:
        """
        Retrieve an item from the cache.
        :param cache_key: Key to return from the cache.
        :return: Dictionary representing the cached object. Empty Dict if doesn't exist in cache.
        """

        with open(self._cache_file, "r") as cache:
            cache_contents = cache.read()
            contents: Dict = json.loads(cache_contents)
            cache = contents.get(cache_key, {})
            result = cache.get(self._LAST_WRITE_KEY, 0), cache.get(self._STORE_KEY, {})
            log.info(f'Returning {len(result[1])} items from cache for cache key: {cache_key}')

        return result

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
                contents: Dict = json.loads(cache.read())
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
                cache.write(json.dumps(contents))
        else:
            log.info('No cached items found to add to cache.')
