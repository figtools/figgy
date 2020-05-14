## Please fill out this file to custom-configure your figgy deployment to meet your needs

## IMPORTANT:
## If you have already provisioned figgy, rearranging values under `encryption_keys` or `user_types` could require
## these resources to be removed/recreated which would probably be a pretty bad thing~!
locals {

  # If you want figgy to create its own S3 bucket, set this to true, then specify the `var.deploy_bucket`
  # with the appropriate deployment bucket name variable. This bucket is used to store figgy deployment artifacts.
  create_deploy_bucket = true

  # If you dot not already have cloudtrail logging enabled, it is required by figgy. We can turn it on for you, or
  # you can enable it on your own.
  configure_cloudtrail = true

  # How many unique roles will figgy users need? Each of these types should map to a particular figgy user story.
  role_types = ["devops", "data", "dba", "sre", "dev"]

  # Encryption keys to allow certain roles to use to encrypt and decrypt secrets stored with figgy. You will map access below
  encryption_keys = ["devops", "data", "app"]

  # List of namespaces at the root level of your parameter store namespace. Figgy (and its users)
  # will ONLY have access to _AT MOST_ configs under these namespaces.
  # ** /shared is required by figgy, all otheres are optional
  root_namespaces = ["/shared", "/app", "/data", "/devops", "/sre", "/dba"]

  # Configure access permissions by mapping your role_types to namespace access levels. Be careful to ensure you
  # don't have any typos here. These must match the above `role_types` and `root_namespaces` configurations
  # Format: Map[str:List[str]], or more specifically Map[role_type:List[namespace]]
  role_to_ns_access = {
    "devops" = ["/app", "/devops", "/data", "/sre"],
    "data" = ["/app", "/data"],
    "sre" = ["/sre", "/app", "/data"],
    "dev" = ["/app"],
    "dba" = ["/dba", "/app"]
  }

  # Map role type access to various encryption keys provisioned by figgy.
  # Format: Map[str:List[str]], specifically Map[role_type:List[encryption_key]]
  role_to_kms_access = {
    "devops" = [ "devops", "app", "data" ]
    "data" = [ "data", "app" ]
    "dba" = [ "data", "app" ]
    "sre" = [ "app" ]
    "dev" = [ "app"]
  }

  # Set to "false" for the "bastion" authentication type, or "true" for all other SSO auth types.
  enable_sso = false

  # SSO Type: Options are okta/google
  sso_type = "okta"

  # Bastion account #. Set to your bastion account # if you are leveraging bastion based authentication. Otherwise ignore.
  bastion_account_number = "816219277933"

  # MFA Enabled - "true/false" - Require MFA for authentication?
  mfa_enabled = true
}