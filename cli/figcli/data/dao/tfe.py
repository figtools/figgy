from figcli.config import *
import boto3
from boto3.dynamodb.conditions import Key, Attr
from typing import List


class TFEDao:
    def __init__(self, mgmt_session: boto3.Session):
        self._mgmt_session = mgmt_session
        self._tfe_cache = self._mgmt_session.resource('dynamodb').Table(TFE_CACHE_TABLE_NAME)

    def get_all_workspaces(self, start_key: str=None) -> List[str]:
        if start_key:
            result = self._tfe_cache.scan(ExclusiveStartKey=start_key)
        else:
            filter_exp = Attr(TFE_TYPE_ATTR_NAME).eq('workspace')
            result = self._tfe_cache.scan(FilterExpression=filter_exp)

        items: List = result["Items"] if result["Items"] else []

        if len(items) == 0:
            return items

        results: List[str] = list(map(lambda x: x["resource_name"], items))

        if 'LastEvaluatedKey' in result:
            results = results + self.get_all_workspaces(start_key=result['LastEvaluatedKey'])

        return results
