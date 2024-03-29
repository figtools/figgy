import boto3
import logging
from typing import List, Dict
from lib.config.constants import *
from lib.models.replication_config import ReplicationType, ReplicationConfig
from lib.data.dynamo.replication_dao import ReplicationDao
from lib.data.ssm.ssm import SsmDao
from lib.models.slack import SlackColor, FigReplicationMessage, SimpleSlackMessage
from lib.svcs.replication import ReplicationService
from lib.svcs.slack import SlackService
from lib.utils.utils import Utils

repl_dao: ReplicationDao = ReplicationDao(boto3.resource('dynamodb'))
ssm: SsmDao = SsmDao(boto3.client('ssm'))
repl_svc: ReplicationService = ReplicationService(repl_dao, ssm)
log = Utils.get_logger(__name__, logging.INFO)

webhook_url = ssm.get_parameter_value(FIGGY_WEBHOOK_URL_PATH)
slack: SlackService = SlackService(webhook_url=webhook_url)

ACCOUNT_ID = ssm.get_parameter_value(ACCOUNT_ID_PS_PATH)


def notify_slack(config: ReplicationConfig, triggering_user: str):
    message = FigReplicationMessage(replication_cfg=config, triggering_user=triggering_user)
    slack.send_message(message)


def parse_user(detail: Dict) -> str:
    """
    Returns the closest match we can find to the user's identity from the event detail.
    :param detail: Event detail provided from SSM event.
    :return: UserId
    """
    principal_id = detail.get('userIdentity', {}).get('principalId')

    if ':' in principal_id:
        return principal_id.split(':')[1]
    else:
        return detail.get('userIdentity', {}).get('arn', 'arn/UnknownUser').split('/')[-1]


def handle(event, context):
    # Don't process other account's events.
    originating_account = event.get('account')
    if originating_account != ACCOUNT_ID:
        log.info(f"{originating_account} != {ACCOUNT_ID}")
        log.info(f"Received event from different account with id: {ACCOUNT_ID}. Skipping this event.")
        return

    try:
        log.info(f"Event: {event}")
        detail = event["detail"]
        action = detail.get("eventName")

        if 'errorMessage' in detail:
            log.info(f'Not processing event due to this being an error event with message: {detail["errorMessage"]}')
            return

        ps_name = detail.get('requestParameters', {}).get('name')
        triggering_user = parse_user(detail)

        if ps_name and action == PUT_PARAM_ACTION:
            repl_configs: List[ReplicationConfig] = repl_dao.get_config_repl_by_source(ps_name)
            merge_configs: List[ReplicationConfig] = repl_dao.get_configs_by_type(ReplicationType(REPL_TYPE_MERGE))
            for config in repl_configs:
                updated = repl_svc.sync_config(config)
                updated and notify_slack(config, triggering_user)  # Notify on update

            for config in merge_configs:
                log.info(f"Evaluating config: {config}")
                if isinstance(config.source, list):
                    for source in config.source:
                        if ps_name in source:
                            updated = repl_svc.sync_config(config)
                            updated and notify_slack(config, triggering_user)
                            continue

        elif action == DELETE_PARAM_ACTION or action == DELETE_PARAMS_ACTION:
            log.info("Delete found, skipping...")
        else:
            log.info(f"Unsupported action type found! --> {action}")

    except Exception as e:
        log.exception("Caught irrecoverable error while executing.")
        title = "Figgy experienced an irrecoverable error!"
        message = f"The following error occurred in an the figgy-ssm-stream-replicator lambda. \n" \
                  f"Figgy is designed to backoff and continually retry in the face of errors. \n" \
                  f"If this appears to be a bug with figgy, please tell us by submitting a GitHub issue!" \
                  f" \n\n```{Utils.printable_exception(e)}```"

        message = SimpleSlackMessage(title=title, message=message, color=SlackColor.RED)
        slack.send_message(message)
        raise e


if __name__ == '__main__':
    handle(None, None)
