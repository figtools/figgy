
PROD_ACCOUNT_ID = "999999999999"
STAGE_ACCOUNT_ID = "999999999999"
QA_ACCOUNT_ID = "999999999999"
DEV_ACCOUNT_ID = "999999999999"

MGMT_ACCOUNT_ID = "999999999999"
MGMT_SNS_ERROR_TOPIC_NAME = 'figgy-error-notifications'
MGMT_SNS_ERROR_TOPIC_ARN = f'arn:aws:sns:us-east-1:{MGMT_ACCOUNT_ID}:{MGMT_SNS_ERROR_TOPIC_NAME}'

AWS_REGION = "us-east-1"
# TODO: SET THIS
PROFILE_SETUP_URL = "SOME_URL"
ENV_SESSION_DURATION = 43200  # 12 hours
BASTION_PROFILE_ENV_NAME = 'FIGGY_AWS_PROFILE'
DEFAULT_USER_NAME = 'FIGGY_DEFAULT_USER'

# ENVS
dev = 'dev'
qa = 'qa'
stage = 'stage'
prod = 'prod'
mgmt = 'mgmt'

standard_envs = [dev, qa, stage, prod]

# THIS MUST BE IN ORDER -- this means that `mgmt` must be last and `prod` must be second to last.
envs = [dev, qa, stage, prod, mgmt]

# Colors:
green = 'green'
blue = 'blue'
red = 'red'

# Role Types
usr_data = 'data'
usr_dev = 'dev'
usr_devops = 'devops'
usr_sre = 'sre'
usr_dba = 'dba'

user_types = [usr_data, usr_dev, usr_devops, usr_data, usr_dba, usr_sre]


# Role name mappings
role_name = {
    usr_dev: 'developer-programmatic',
    usr_data: 'data-programmatic',
    usr_devops: 'devops-programmatic',
    usr_dba: 'dba-programmatic',
    usr_sre: 'sre-programmatic',
}

ACCOUNT_ID_MAP = {
    dev: DEV_ACCOUNT_ID,
    qa: QA_ACCOUNT_ID,
    stage: STAGE_ACCOUNT_ID,
    prod: PROD_ACCOUNT_ID,
    mgmt: MGMT_ACCOUNT_ID
}

ROLE_ARN_MAP = {
    dev: f"arn:aws:iam::{DEV_ACCOUNT_ID}:role/",
    qa: f"arn:aws:iam::{QA_ACCOUNT_ID}:role/",
    stage: f"arn:aws:iam::{STAGE_ACCOUNT_ID}:role/",
    prod: f"arn:aws:iam::{PROD_ACCOUNT_ID}:role/",
    mgmt: f"arn:aws:iam::{MGMT_ACCOUNT_ID}:role/"
}
