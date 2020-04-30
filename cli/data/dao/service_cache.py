from config import *
from data.models.service_cache_item import ServiceCacheItem
from typing import List, Set


class ServiceCacheDao:

    def __init__(self, dynamo_resource):
        self._dynamo_resource = dynamo_resource
        self._service_cache_table = self._dynamo_resource.Table(SERVICE_NAME_CACHE_TABLE_NAME)

    def get_all_service_names(self, start_key: str = None) -> Set[str]:
        """
        Retrieve all key names from the Dynamo DB config-cache table in each account. Much more efficient than
        querying SSM directly.
        Args:
            start_key: Optional: Is used for recursive paginated lookups to get the full data set. This should not
            be passed in by the user.
        Returns:

        """
        if start_key:
            result = self._service_cache_table.scan(ExclusiveStartKey=start_key)
        else:
            result = self._service_cache_table.scan()

        service_names: Set[str] = set()
        [service_names.add(item.get('service_name', '')) for item in result.get('Items', [])]

        if 'LastEvaluatedKey' in result:
            service_names = service_names | self.get_all_service_names(start_key=result['LastEvaluatedKey'])

        return service_names

    def get_services_and_clusters(self, start_key: str = None) -> Set[ServiceCacheItem]:
        """
           Retrieve all key names from the Dynamo DB config-cache table in each account. Much more efficient than
           querying SSM directly.
           Args:
               start_key: Optional: Is used for recursive paginated lookups to get the full data set. This should not
               be passed in by the user.
           Returns: Set[ServiceCacheItem] representing all items in the cache table.
       """
        if start_key:
            result = self._service_cache_table.scan(ExclusiveStartKey=start_key)
        else:
            result = self._service_cache_table.scan()

        items: Set[ServiceCacheItem] = set()
        [items.add(ServiceCacheItem.from_boto3_item(item)) for item in result.get('Items', [])]

        if 'LastEvaluatedKey' in result:
            items = items | self.get_all_service_names(start_key=result['LastEvaluatedKey'])

        return items
