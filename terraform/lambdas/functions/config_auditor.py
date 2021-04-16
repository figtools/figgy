import logging
import time

import boto3

from config.constants import *
from lib.data.dynamo.audit_dao import AuditDao
from lib.data.ssm import SsmDao
from lib.models.slack import FigDeletedMessage, SlackColor, SimpleSlackMessage
from lib.svcs.slack import SlackService
from lib.utils.ssm_event_parser import SSMErrorDetected, SSMEvent
from lib.utils.utils import Utils

log = Utils.get_logger(__name__, logging.INFO)

dynamo_resource = boto3.resource("dynamodb")
audit: AuditDao = AuditDao(dynamo_resource)
ssm_client = boto3.client('ssm')
ssm = SsmDao(ssm_client)
webhook_url = ssm.get_parameter_value(FIGGY_WEBHOOK_URL_PATH)
slack: SlackService = SlackService(webhook_url=webhook_url)

ACCOUNT_ID = ssm.get_parameter_value(ACCOUNT_ID_PS_PATH)
ACCOUNT_ENV = ssm.get_parameter_value(ACCOUNT_ENV_PS_PATH)
NOTIFY_DELETES = ssm.get_parameter_value(NOTIFY_DELETES_PS_PATH)
NOTIFY_DELETES = NOTIFY_DELETES.lower() == "true" if NOTIFY_DELETES else False

FIGGY_NAMESPACES = ssm.get_parameter_value(FIGGY_NAMESPACES_PATH)
CLEANUP_INTERVAL = 60 * 60  # Cleanup hourly
LAST_CLEANUP = 0


def notify_delete(ps_name: str, user: str):
    if NOTIFY_DELETES:
        slack.send_message(
            FigDeletedMessage(name=ps_name, user=user, environment=ACCOUNT_ENV)
        )


def handle(event, context):
    global LAST_CLEANUP

    # Don't process other account's events.
    originating_account = event.get('account')
    if originating_account != ACCOUNT_ID:
        log.info(f"Received event from different account with id: {ACCOUNT_ID}. Skipping this event.")
        return

    try:
        log.info(f'Got event: {event}')
        event = SSMEvent(event)

        log.info(f"Got user: {event.user}, action: {event.action} for parameter(s) {event.parameters}")

        for ps_name in event.parameters:
            ps_name = f'/{ps_name}' if not ps_name.startswith('/') else ps_name
            matching_ns = [ns for ns in FIGGY_NAMESPACES if ps_name.startswith(ns)]

            if not matching_ns:
                log.info(f'PS Name: {ps_name} - is not maintained by Figgy. Skipping..')
                continue

            if event.action == DELETE_PARAM_ACTION or event.action == DELETE_PARAMS_ACTION:
                audit.put_delete_log(event.user, event.action, ps_name, timestamp=event.time)
                notify_delete(ps_name, event.user)
            elif event.action == PUT_PARAM_ACTION:
                if not event.value:
                    event.value = ssm.get_parameter_value_encrypted(ps_name)

                audit.put_audit_log(
                    event.user,
                    event.action,
                    ps_name,
                    event.value,
                    event.type,
                    event.key_id,
                    event.description,
                    event.version,
                    timestamp=event.time,
                )
            else:
                log.info(f"Unsupported action type found! --> {event.action}")

        # This will occasionally cleanup parameters with the explict value of DELETE_ME.
        # Great for testing and adding PS parameters you don't want to be restored later on.
        if time.time() - CLEANUP_INTERVAL > LAST_CLEANUP:
            log.info("Cleaning up.")
            audit.cleanup_test_logs()
            LAST_CLEANUP = time.time()

    except SSMErrorDetected as e:
        log.info(f'Not processing event due to error Message {event.error_message} and Code: {event.error_code}')
        return
    except Exception as e:
        log.error(e)
        message = f"The following error occurred in an the figgy-ssm-stream-replicator lambda. " \
                  f"If this appears to be a bug with Figgy, please tell us by submitting a GitHub issue!" \
                  f" \n\n{Utils.printable_exception(e)}"

        title = "Figgy experienced an irrecoverable error!"
        message = SimpleSlackMessage(
            title=title,
            message=message,
            color=SlackColor.RED
        )
        slack.send_message(message)
        raise e


if __name__ == "__main__":
    handle(None, None)
