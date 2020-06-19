# Setting Figgy defaults to reduce user configuration requirements.
Fill this file in and place it under ~/.figgy/config

THIS FILE IS ENTIRELY OPTIONAL. If you do not provide this file, Figgy will just prompt you for 
what it needs. This is for convenience when distributing figgy across large groups who may not
know what the OKTA "app_link" is or the Google Identity Provider ID, etc.
 ```ini
[FIGGY]
mfa_enabled = false
colors_enabled = true
aws_region = us-east-1

# User will ALWAYS be prompted to report errors to prevent accidental reporting.
# If set to false, the user will never be prompted. 
report_errors = true

# Save your MFA secret to your keychain and have figgy automatically generate 
# one time pass codes on your behalf to submit for SSO authentication.
auto_mfa = true

# You may remove this is you do not use OKTA
[OKTA]
# Find this on your OKTA AWS applicatoin page on the General tab. It's labeled as EMBED LINK:
app_link = https://your-domain.okta.com/home/amazon_aws/AsdF1afak123145faf1/123
factor_type = GOOGLE

# You may remove this if you don't use GOOGLE
[GOOGLE]
# admin.google.com -> ||| (top left) ->  Security -> Settings -> Set up single sign-on (SSO) for SAML
# applications (expand) -> SSO URL -> idp?idpid=B13asdfe3
identity_provider_id = B13asdfe3

# admin.google.com -> ||| (top left) ->  Apps -> SAML Apps -> Your AWS App 
# -> LOOK AT URL -> ...:service=12345678910
service_provider_id = 12345678910

# You may remove this if you don't use Bastion based authentication
[BASTION]
# AWS CLI required https://aws.amazon.com/cli/
# Name of profile in your ~/.aws/credentials file that has AWS Access Key associated with your 
# Figgy bastion user. You can create this profile by running `aws configure --profile figgy-bastion`
profile = 'figgy-bastion'
``` 


