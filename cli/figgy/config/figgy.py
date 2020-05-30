from enum import Enum

"""
The below classes represent a figgy config file found under ~/.figgy/config that provides defaults and override values
so users don't have to go through the full configuration workflow when running `figgy --configure`
"""


class ConfigSection:
    NAME = None


class Config:
    class Section:
        class Okta(ConfigSection, Enum):
            NAME = 'OKTA'
            APP_LINK = 'app_link'
            FACTOR_TYPE = 'factor_type'

        class Google(ConfigSection, Enum):
            NAME = 'GOOGLE'
            IDP_ID = 'identity_provider_id'
            SP_ID = 'service_provider_id'

        class Bastion(ConfigSection, Enum):
            NAME = 'BASTION'
            PROFILE = 'profile'

        class Figgy(ConfigSection, Enum):
            NAME = 'FIGGY'
            MFA_ENABLED = 'mfa_enabled'
            AUTO_MFA = 'auto_mfa'
            COLORS_ENABLED = 'colors_enabled'
            REPORT_ERRORS = 'report_errors'
            AWS_REGION = 'aws_region'


EMPTY_CONFIG = """
[FIGGY]
mfa_enabled = false
auto_mfa = false
colors_enabled = true
report_errors = true
aws_region = us-east-1

[OKTA]
app_link = https://your-domain.okta.com/home/amazon_aws/0oaaqxeiciFzAVassP4x6/123
factor_type = GOOGLE

[GOOGLE]
identity_provider_id = N0tre9le3
service_provider_id = 12345678010

[BASTION]
profile = default

"""
