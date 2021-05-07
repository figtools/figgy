import logging
import json
from typing import Dict

import boto3
import base64
import gzip

from config.constants import *
from lib.data.dynamo.usage_tracker_dao import UsageTrackerDao
from lib.data.dynamo.user_cache_dao import UserCacheDao
from lib.data.ssm import SsmDao
from lib.models.slack import SlackColor, SimpleSlackMessage
from lib.svcs.slack import SlackService
from lib.utils.ssm_event_parser import SSMEvent
from lib.utils.utils import Utils

log = Utils.get_logger(__name__, logging.INFO)

# Boto3 resources
dynamo_resource = boto3.resource("dynamodb")
ssm_client = boto3.client('ssm')

# Daos
usage_tracker: UsageTrackerDao = UsageTrackerDao(dynamo_resource)
user_cache: UserCacheDao = UserCacheDao(dynamo_resource)
ssm = SsmDao(ssm_client)

webhook_url = ssm.get_parameter_value(FIGGY_WEBHOOK_URL_PATH)
slack: SlackService = SlackService(webhook_url=webhook_url)

ACCOUNT_ID = ssm.get_parameter_value(ACCOUNT_ID_PS_PATH)
ACCOUNT_ENV = ssm.get_parameter_value(ACCOUNT_ENV_PS_PATH)
NOTIFY_DELETES = ssm.get_parameter_value(NOTIFY_DELETES_PS_PATH)
NOTIFY_DELETES = NOTIFY_DELETES.lower() == "true" if NOTIFY_DELETES else False

FIGGY_NAMESPACES = json.loads(ssm.get_parameter_value(FIGGY_NAMESPACES_PATH))
CLEANUP_INTERVAL = 60 * 60  # Cleanup hourly
LAST_CLEANUP = 0


def handle(event, context):
    global LAST_CLEANUP
    log.info(f"Event: {event}")
    data = event.get('awslogs', {}).get('data')
    bytes = base64.b64decode(data)
    decompressed = gzip.decompress(bytes)
    log.info(f'Decompressed: {decompressed}')
    if data:
        data: Dict = json.loads(decompressed)
        log.info(f'Got data: {data}')
    else:
        raise ValueError(f"Unable decode and decompress event data: {event.get(data)}")

    log_events = data.get('logEvents')
    log.info(f'Got events: {log_events}')
    for log_event in log_events:
        log.info(f'Processing event: {log_event}')
        message = json.loads(log_event.get('message'))

        log.info(f"Got message: {message}")
        # Don't process other account's events.
        originating_account = message.get('userIdentity', {}).get('accountId')
        if originating_account != ACCOUNT_ID:
            log.info(f"Received event from account {originating_account}, only processing events from account with "
                     f"id: {ACCOUNT_ID}. Skipping this event.")
            continue

        try:
            ssm_event = SSMEvent(message)

            if ssm_event.is_error():
                log.info(f'Not processing event due to error Message {ssm_event.error_message} '
                         f'and Code: {ssm_event.error_code}')
                continue

            log.info(f"Got user: {ssm_event.user}, action: {ssm_event.action} for parameter(s) {ssm_event.parameters}")
            if ssm_event.user.startswith('figgy') and ssm_event.user != 'figgy-demo@mailinator.com':
                log.info(f'Found event from figgy, not logging.')
                return

            for ps_name in ssm_event.parameters:
                name = f'/{ps_name}' if not ps_name.startswith('/') else ps_name
                matching_ns = [ns for ns in FIGGY_NAMESPACES if ps_name.startswith(ns)]

                if matching_ns:
                    log.info(f"Found GET event for matching namespace: {matching_ns} and name: {name}")
                    usage_tracker.add_usage_log(name, ssm_event.user, ssm_event.time)
                    user_cache.add_user_to_cache(ssm_event.user, state=USER_CACHE_STATE_ACTIVE)
                else:
                    log.info(f'PS Name: {name} - {FIGGY_NAMESPACES} - no match found. ')


        except Exception as e:
            log.exception("Caught irrecoverable error while executing.")
            message = f"The following error occurred in an the figgy-config-usage-tracker lambda. " \
                      f"If this appears to be a bug with Figgy, please tell us by submitting a GitHub issue!" \
                      f" \n\n{Utils.printable_exception(e)}"

            title = "Figgy experienced an irrecoverable error!"
            message = SimpleSlackMessage(
                title=title,
                message=message,
                color=SlackColor.RED
            )
            slack.send_message(message)
            continue


if __name__ == "__main__":
    handle(None, None)
