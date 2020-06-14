# THIS MUST MATCH devops.ci.lambdas/lambdas/python/parameter_store_auditor/config.py's value!!!
### For PS items stored with this value, we will auto-clean them up from our audit table. Used for automated E2E testing.
DELETE_ME_VALUE = 'DELETE_ME'   ### <-- use this for ALL VALUES
MFA_USER_ENV_KEY = 'MFA_USER'
MFA_SECRET_ENV_KEY = 'MFA_SECRET'

# Env vars
GOOGLE_SSO_USER = 'GOOGLE_SSO_USER'
GOOGLE_SSO_PASSWORD = 'GOOGLE_SSO_PASSWORD'
GOOGLE_IDP_ID = 'GOOGLE_IDP_ID'
GOOGLE_SP_ID = 'GOOGLE_SP_ID'

OKTA_SSO_USER = 'OKTA_SSO_USER'
OKTA_SSO_PASSWORD = 'OKTA_SSO_PASSWORD'
OKTA_EMBED_URL = 'OKTA_EMBED_URL'
OKTA_MFA_SECRET = 'OKTA_MFA_SECRET'


# Variables
param_1 = '/shared/test/automated_test/param_1'
param_test_prefix = '/shared/test2/automated_test/'
dump_prefix = '/shared/test/automated_test/'
data_param_1 = '/data/test/automated_test/parm_1'
devops_param_1 = '/devops/test/automated_test/param_1'

# Values
param_1_val = DELETE_ME_VALUE
data_param_1_val = DELETE_ME_VALUE
devops_param_1_val = DELETE_ME_VALUE


# Desc
param_1_desc = 'desc1'
data_param_1_desc = 'datadesc1'
devops_param_1_desc = 'devopsdesc1'


# Share destination
automated_test_dest_1 = '/app/automated-test/dest/1'


# Others
DEFAULT_ENV = 'stage'