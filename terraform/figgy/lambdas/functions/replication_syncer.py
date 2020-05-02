import time
import boto3

from lib.data.dynamo.replication_dao import ReplicationDao
from lib.data.ssm.ssm import SsmDao
from lib.svcs.replication import ReplicationService

repl_dao: ReplicationDao = ReplicationDao(boto3.resource('dynamodb'))
ssm: SsmDao = SsmDao(boto3.client('ssm'))
repl_svc: ReplicationService = ReplicationService(repl_dao, ssm)


def handle(event, context):

    repl_configs = repl_dao.get_all()
    for config in repl_configs:
        repl_svc.sync_config(config)
        time.sleep(.15)  # This is to throttle PS API Calls to prevent overloading the API.


if __name__ == '__main__':
    handle(None, None)
