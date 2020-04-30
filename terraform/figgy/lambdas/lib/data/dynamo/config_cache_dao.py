import time
from typing import Set

from config.constants import *


class ConfigCacheDao:

    def __init__(self, ddb_resource):
        self._dynamo_resource = ddb_resource
        self._table = self._dynamo_resource.Table(CONFIG_CACHE_TABLE_NAME)

    def get_cached_names(self) -> Set[str]:
        all_items = self._table.scan()
        return set([item['parameter_name'] for item in all_items['Items']])

    def delete_from_cache(self, name: str):
        self._table.delete_item(Key={
            CONFIG_CACHE_PARAM_NAME_KEY: name
        })

    def put_in_cache(self, name: str):
        item = {
            CONFIG_CACHE_PARAM_NAME_KEY: name,
            CONFIG_CACHE_LAST_UPDATED_KEY: int(time.time() * 1000)
        }

        self._table.put_item(Item=item)
