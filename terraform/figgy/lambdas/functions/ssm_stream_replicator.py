import boto3
import logging
from typing import List
from config.constants import *
from lib.models.replication_config import ReplicationType, ReplicationConfig
from lib.data.dynamo.replication_dao import ReplicationDao
from lib.data.ssm.ssm import SsmDao
from lib.svcs.replication import ReplicationService
from lib.utils.utils import Utils

repl_dao: ReplicationDao = ReplicationDao(boto3.resource('dynamodb'))
ssm: SsmDao = SsmDao(boto3.client('ssm'))
repl_svc: ReplicationService = ReplicationService(repl_dao, ssm)
log = Utils.get_logger(__name__, logging.INFO)


def handle(event, context):
    log.info(f"Event: {event}")
    detail = event["detail"]
    action = detail["eventName"]

    if 'errorMessage' in detail:
        log.info(f'Not processing event due to this being an error event with message: {detail["errorMessage"]}')
        return

    ps_name = detail.get('requestParameters', {}).get('name')

    if ps_name and action == PUT_PARAM_ACTION:
        repl_configs: List[ReplicationConfig] = repl_dao.get_config_repl_by_source(ps_name)
        merge_configs: List[ReplicationConfig] = repl_dao.get_configs_by_type(ReplicationType(REPL_TYPE_MERGE))
        for config in repl_configs:
            repl_svc.sync_config(config)

        for config in merge_configs:
            log.info(f"Evaluating config: {config}")
            if isinstance(config.source, list):
                for source in config.source:
                    if ps_name in source:
                        repl_svc.sync_config(config)
                        continue
    elif action == DELETE_PARAM_ACTION or action == DELETE_PARAMS_ACTION:
        log.info("Delete found, skipping...")
    else:
        log.info(f"Unsupported action type found! --> {action}")


if __name__ == '__main__':
    handle(None, None)
