from config.constants import MGMT_ACCOUNT_ID, HOME

# OKTA Constants
OKTA_BASE_URL = "dev-216899.okta.com"
OKTA_INTEGRATED_AWS_ACCOUNT_ID = MGMT_ACCOUNT_ID
OKTA_FACTOR = "GOOGLE"
OKTA_APP_LINK = "https://dev-216899-admin.okta.com/home/amazon_aws/0oa1gkuwcfsE55aFY0h8/272"
OKTA_SESSION_DURATION = 43200
OKTA_PROVIDER_NAME = "dev-216899-admin"
OKTA_PRINCIPAL_ARN = f"arn:aws:iam::{OKTA_INTEGRATED_AWS_ACCOUNT_ID}:saml-provider/{OKTA_PROVIDER_NAME}"
FIGGY_KEYRING_NAMESPACE = "figgy"
FIGGY_KEYRING_ASSERTION_NAME = "okta_assertion"
OKTA_SESSION_CACHE_PATH = f"{HOME}/.figgy/devops/cache/okta/session"