import boto3
from lib.data.dynamo.replication_dao import ReplicationDao
from lib.data.ssm.ssm import SsmDao
from lib.svcs.replication import ReplicationService


repl_dao: ReplicationDao = None
ssm: SsmDao = None
repl_svc: ReplicationService = None


def lazy_init():
    global ssm
    global repl_dao
    global repl_svc

    if ssm is None:
        ssm = SsmDao(boto3.client('ssm'))

    if repl_dao is None:
        repl_dao = ReplicationDao(boto3.resource('dynamodb'))

    if repl_svc is None:
        repl_svc = ReplicationService(repl_dao, ssm)
