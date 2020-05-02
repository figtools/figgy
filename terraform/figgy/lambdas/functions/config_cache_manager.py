from typing import Set

import boto3
import logging

from lib.utils.utils import Utils
from config.constants import *
from lib.data.dynamo.config_cache_dao import ConfigCacheDao, ConfigItem

dynamo_resource = boto3.resource("dynamodb")
log = Utils.get_logger(__name__, logging.INFO)


def handle(event, context):
    log.info(f"Event: {event}")
    cache_dao: ConfigCacheDao = ConfigCacheDao(dynamo_resource)

    detail = event["detail"]
    action = detail["eventName"]
    ps_name = detail.get('requestParameters', {}).get('name')

    if not ps_name:
        raise ValueError("ParameterStore name is missing from event!")

    if action == DELETE_PARAM_ACTION or action == DELETE_PARAMS_ACTION:
        log.info(f"Deleting from cache: {ps_name}")
        items: Set[ConfigItem] = cache_dao.get_items(ps_name)
        [cache_dao.mark_deleted(item) for item in items]
    elif action == PUT_PARAM_ACTION:
        log.info(f"Putting in cache: {ps_name}")
        cache_dao.put_in_cache(ps_name)
    else:
        log.info(f"Unsupported action type found! --> {action}")


if __name__ == "__main__":
    handle(None, None)
