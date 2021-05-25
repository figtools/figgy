import json
import logging

import boto3

from lib.config.constants import *
from lib.data.dynamo.usage_tracker_dao import UsageTrackerDao
from lib.data.dynamo.user_cache_dao import UserCacheDao
from lib.data.ssm import SsmDao
from lib.models.slack import SlackColor, SimpleSlackMessage
from lib.svcs.s3 import S3Service
from lib.svcs.slack import SlackService
from lib.utils.cloudtrail_parser import CloudtrailParser
from lib.utils.utils import Utils

log = Utils.get_logger(__name__, logging.INFO)

# Boto3 resources
dynamo_resource = boto3.resource("dynamodb")
ssm_client = boto3.client('ssm')
s3_client = boto3.client('s3')

# DAOs / SVCS
usage_tracker: UsageTrackerDao = UsageTrackerDao(dynamo_resource)
user_cache: UserCacheDao = UserCacheDao(dynamo_resource)
ssm = SsmDao(ssm_client)
s3_svc = S3Service(s3_client)

webhook_url = ssm.get_parameter_value(FIGGY_WEBHOOK_URL_PATH)
slack: SlackService = SlackService(webhook_url=webhook_url)

ACCOUNT_ID = ssm.get_parameter_value(ACCOUNT_ID_PS_PATH)
ACCOUNT_ENV = ssm.get_parameter_value(ACCOUNT_ENV_PS_PATH)
NOTIFY_DELETES = ssm.get_parameter_value(NOTIFY_DELETES_PS_PATH)
NOTIFY_DELETES = NOTIFY_DELETES.lower() == "true" if NOTIFY_DELETES else False

FIGGY_NAMESPACES = json.loads(ssm.get_parameter_value(FIGGY_NAMESPACES_PATH))


def handle(event, context):
    records = event.get('Records', [])

    for record in records:
        s3_record = record.get("s3", {})
        bucket = s3_record.get('bucket', {}).get('name')
        key = s3_record.get('object', {}).get('key')
        download_dest = f'/tmp/{key.split("/")[-1]}'
        s3_svc.download_file(bucket=bucket, obj_key=key, download_destination=f'/tmp/{key.split("/")[-1]}')
        parser: CloudtrailParser = CloudtrailParser(download_dest)

        try:
            for ssm_event in parser.next_ssm_event():
                if ssm_event.is_error():
                    log.info(f'Not processing event due to error Message {ssm_event.error_message} '
                             f'and Code: {ssm_event.error_code}')
                    continue

                log.info(f"Got user: {ssm_event.user}, action: {ssm_event.action} for parameter(s) {ssm_event.parameters}")

                if ssm_event.user.startswith('figgy') and ssm_event.user != 'figgy-demo@mailinator.com':
                    log.info(f'Found event from figgy, not logging.')
                    continue

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
