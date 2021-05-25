import time

from lib.config.constants import *


class UsageTrackerDao:
    """
    Supports operations on the figgy-config-usage-tracker ddb table.
    """

    def __init__(self, dynamo_resource):
        self._dynamo_resource = dynamo_resource
        self._table = self._dynamo_resource.Table(CONFIG_USAGE_TABLE_NAME)

    def add_usage_log(self, parameter_name: str, user: str, timestamp: int = int(time.time() * 1000)):
        item = {
            CONFIG_USAGE_PARAMETER_KEY: parameter_name,
            CONFIG_USAGE_USER_KEY: user,
            CONFIG_USAGE_LAST_UPDATED_KEY: timestamp,
            CONFIG_USAGE_EMPTY_KEY: CONFIG_USAGE_EMPTY_IDX_VALUE,
        }

        self._table.put_item(Item=item)
