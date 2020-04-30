import boto3

from config.constants import *
from lib.data.dynamo.config_cache_dao import ConfigCacheDao

dynamo_resource = boto3.resource("dynamodb")


def handle(event, context):
    print(f"Event: {event}")
    cache_dao: ConfigCacheDao = ConfigCacheDao(dynamo_resource)

    detail = event["detail"]
    action = detail["eventName"]
    ps_name = detail.get('requestParameters', {}).get('name')

    if not ps_name:
        raise ValueError("ParameterStore name is missing from event!")

    if action == DELETE_PARAM_ACTION or action == DELETE_PARAMS_ACTION:
        print(f"Deleting from cache: {ps_name}")
        cache_dao.delete_from_cache(ps_name)
    elif action == PUT_PARAM_ACTION:
        print(f"Putting in cache: {ps_name}")
        cache_dao.put_in_cache(ps_name)
    else:
        print(f"Unsupported action type found! --> {action}")


if __name__ == "__main__":
    handle(None, None)
