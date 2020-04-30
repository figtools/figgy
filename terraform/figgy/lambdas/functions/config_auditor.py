import random
import boto3

from config.constants import *
from lib.data.dynamo.audit_dao import AuditDao

dynamo_resource = boto3.resource("dynamodb")
audit: AuditDao = AuditDao(dynamo_resource)


def handle(event, context):
    print(f"Event: {event}")
    detail = event["detail"]
    user_arn = detail["userIdentity"]["arn"]
    user = user_arn.split("/")[-1:][0]
    action = detail["eventName"]

    if 'errorMessage' in detail:
        print(f'Not processing event due to this being an error event with message: {detail["errorMessage"]}')
        return

    ps_name = detail.get('requestParameters', {}).get('name')

    if ps_name:
        if action == DELETE_PARAM_ACTION or action == DELETE_PARAMS_ACTION:
            audit.put_delete_log(user, action, ps_name)
        elif action == PUT_PARAM_ACTION:
            ps_value = (
                detail["requestParameters"]["value"]
                if "value" in detail["requestParameters"]
                else None
            )
            ps_type = detail["requestParameters"]["type"]
            ps_description = (
                detail["requestParameters"]["description"]
                if "description" in detail["requestParameters"]
                else None
            )
            ps_version = detail["responseElements"]["version"]
            ps_key_id = (
                detail["requestParameters"]["keyId"]
                if "keyId" in detail["requestParameters"]
                else None
            )

            if not ps_value:
                ps_value = get_parameter_value(ps_name)

            audit.put_audit_log(
                user,
                action,
                ps_name,
                ps_value,
                ps_type,
                ps_key_id,
                ps_description,
                ps_version,
            )
        else:
            print(f"Unsupported action type found! --> {action}")

        # this requires a table scan, so don't do this _EVERY_ run. No big deal. 1 in 30 chance.
    if random.randint(1, 30) == 3:
        print("Cleaning up.")
        audit.cleanup_test_logs()
    else:
        print("Skipping cleanup.")


def get_parameter_value(key):
    ssm = boto3.client("ssm")
    parameter = ssm.get_parameter(Name=key, WithDecryption=False)
    return parameter["Parameter"]["Value"]


if __name__ == "__main__":
    handle(None, None)
