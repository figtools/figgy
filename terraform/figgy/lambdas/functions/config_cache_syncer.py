import boto3
import logging
from config.constants import *
from lib.data.dynamo.config_cache_dao import ConfigCacheDao
from lib.data.ssm.ssm import SsmDao
from lib.utils.utils import Utils

dynamo_resource = boto3.resource("dynamodb")
ssm_client = boto3.client('ssm')
ssm_dao = SsmDao(ssm_client)
cache_dao: ConfigCacheDao = ConfigCacheDao(dynamo_resource)
log = Utils.get_logger(__name__, logging.INFO)


def handle(event, context):
    param_names = ssm_dao.get_all_param_names(PS_ROOT_NAMESPACES)
    cached_names = cache_dao.get_cached_names()

    missing_params = param_names.difference(cached_names)
    to_delete = cached_names.difference(param_names)

    for param in missing_params:
        log.info(f"Storing in cache: {param}")
        cache_dao.put_in_cache(param)

    for param in to_delete:
        log.info(f"Deleting from cache: {param}")
        cache_dao.delete_from_cache(param)


if __name__ == "__main__":
    handle(None, None)
