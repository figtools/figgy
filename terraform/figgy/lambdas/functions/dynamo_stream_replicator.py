import boto3
import logging
from config.constants import *
from lib.models.replication_config import ReplicationConfig
from lib.data.dynamo.replication_dao import ReplicationDao
from lib.data.ssm.ssm import SsmDao
from lib.svcs.replication import ReplicationService
from lib.utils.utils import Utils

repl_dao: ReplicationDao = ReplicationDao(boto3.resource('dynamodb'))
ssm: SsmDao = SsmDao(boto3.client('ssm'))
repl_svc: ReplicationService = ReplicationService(repl_dao, ssm)

log = Utils.get_logger(__name__, logging.INFO)

def handle(event, context):
    log.info(f"Got Event: {event} with context {context}")

    records = event.get('Records', [])
    for record in records:
        event_name = record.get("eventName")
        # Only resync on adds / updates, never on deletes.
        if event_name != 'REMOVE':
            ddb_record = record.get("dynamodb", {})
            keys = ddb_record.get("Keys", {})
            destination = keys.get(REPL_DEST_KEY_NAME, {}).get("S", None)
            run_env = keys.get(REPL_RUN_ENV_KEY_NAME, {}).get("S", None)
            if destination and run_env:
                log.info(f"Record updated with key: {destination} and run_env: {run_env}")
                config: ReplicationConfig = repl_dao.get_config_repl(destination, run_env)
                log.info(f"Got config: {config}, syncing...")
                repl_svc.sync_config(config)
        else:
            log.info("Event is a delete event, skipping!")


if __name__ == '__main__':
    handle(None, None)
