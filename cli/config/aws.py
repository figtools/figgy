# TODO TURN THIS INTO A CONFIG
PROD_ACCOUNT_ID = "816636370623"
STAGE_ACCOUNT_ID = "750075891372"
QA_ACCOUNT_ID = "713117490776"
DEV_ACCOUNT_ID = "106481321259"
MGMT_ACCOUNT_ID = "816219277933"

MGMT_SNS_ERROR_TOPIC_NAME = 'figgy-error-notifications'
MGMT_SNS_ERROR_TOPIC_ARN = f'arn:aws:sns:us-east-1:{MGMT_ACCOUNT_ID}:{MGMT_SNS_ERROR_TOPIC_NAME}'

AWS_REGION = "us-east-1"
ENV_SESSION_DURATION = 43200  # 12 hours
BASTION_PROFILE_ENV_NAME = 'FIGGY_AWS_PROFILE'
DEFAULT_USER_NAME = 'FIGGY_DEFAULT_USER'

# Colors:
green = 'green'
blue = 'blue'
red = 'red'
#
# # ENVS
# dev = 'dev'
# qa = 'qa'
# stage = 'stage'
# prod = 'prod'
# mgmt = 'mgmt'
#
# # THIS MUST BE IN ORDER -- this means that `mgmt` must be last and `prod` must be second to last.
# envs = [dev, qa, stage, prod, mgmt]
#
# # Role Types
# usr_data = 'data'
# usr_dev = 'dev'
# usr_devops = 'devops'
# usr_sre = 'sre'
# usr_dba = 'dba'
#
# user_types = [usr_data, usr_dev, usr_devops, usr_data, usr_dba, usr_sre]
#
# ACCOUNT_ID_MAP = {
#     dev: DEV_ACCOUNT_ID,
#     qa: QA_ACCOUNT_ID,
#     stage: STAGE_ACCOUNT_ID,
#     prod: PROD_ACCOUNT_ID,
#     mgmt: MGMT_ACCOUNT_ID
# }
#
# ROLE_ARN_MAP = {
#     dev: f"arn:aws:iam::{DEV_ACCOUNT_ID}:role/",
#     qa: f"arn:aws:iam::{QA_ACCOUNT_ID}:role/",
#     stage: f"arn:aws:iam::{STAGE_ACCOUNT_ID}:role/",
#     prod: f"arn:aws:iam::{PROD_ACCOUNT_ID}:role/",
#     mgmt: f"arn:aws:iam::{MGMT_ACCOUNT_ID}:role/"
# }
