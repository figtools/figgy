from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class ServiceCacheItem:
    # Column mappings
    CLUSTER_ARN_KEY = 'cluster_arn'
    SERVICE_NAME_KEY = 'service_name'

    # Properties
    cluster_name: str
    service_name: str

    @staticmethod
    def from_boto3_item(item: Dict):
        service = item.get(ServiceCacheItem.SERVICE_NAME_KEY)
        cluster = item.get(ServiceCacheItem.CLUSTER_ARN_KEY)
        return ServiceCacheItem(cluster_name=cluster, service_name=service)
