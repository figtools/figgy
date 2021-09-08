## Please fill out this file to custom-configure your figgy deployment to meet your needs

## IMPORTANT:
## If you have already provisioned figgy, rearranging values under `encryption_keys` or `user_types` could require
## these resources to be removed/recreated which would probably be a pretty bad thing~!
locals {
  cfgs = {

    # Figgy needs to create a S3 bucket to deploy its lambdas and to store temporary logs (that are cleaned up after one day).
    # Add something here if you want to prefix the bucket with a friendly name, otherwise leave empty. The default bucket name will be:
    # 'figgy-${aws_region}-${random-str}'
    s3_bucket_prefix = ""

    # How many unique roles will figgy users need? Each of these types should map to a particular figgy user story.
    role_types = ["admin", "devops", "data", "dba", "sre", "dev"]

    # Encryption keys to allow certain roles to use to encrypt and decrypt secrets stored with figgy.
    # You will map access below
    encryption_keys = ["app", "devops", "data"]

    # List of namespaces at the root level of your parameter store namespace. Figgy (and its users)
    # will ONLY have access to _AT MOST_ configs under these namespaces.
    # ** /shared is required by figgy, all others are optional
    root_namespaces = ["/shared", "/app", "/data", "/devops", "/sre", "/dba"]

    # This namespace is where _all_ service specific configurations will be stored. Must be one of the above listed
    # namespaces. We recommend keeping /app
    service_namespace = "/app"

    # Configure access permissions by mapping your role_types to namespace access levels. Be careful to ensure you
    # don't have any typos here. These must match the above `role_types` and `root_namespaces` configurations
    # Format: Map[str:List[str]], or more specifically Map[role_type:List[namespace]]
    role_to_ns_access = {
      "admin" = ["/shared", "/app", "/data", "/devops", "/sre", "/dba"]
      "devops" = ["/shared", "/app", "/devops", "/data", "/sre"],
      "data" = ["/shared", "/app", "/data"],
      "sre" = ["/shared", "/sre", "/app", "/data"],
      "dev" = ["/shared", "/app",],
      "dba" = ["/shared", "/dba", "/app"]
    }

    # Map role type access to various encryption keys provisioned by figgy.
    # Format: Map[str:List[str]], specifically Map[role_type:List[encryption_key]]
    role_to_kms_access = {
      "admin" = ["app", "devops", "data"]
      "devops" = [ "devops", "app", "data" ]
      "data" = [ "data", "app" ]
      "dba" = [ "data", "app" ]
      "sre" = [ "app" ]
      "dev" = [ "app"]
    }

    # Options: "okta", "google", "bastion", "standard"
    auth_type = "bastion"

    # Environments with replication key access. This will give all user types access to the figgy replication key.
    # and enable users to run services locally and decrypt secrets shared with their application. Ideal for
    # local development. More details: https://www.figgy.dev/docs/advanced/confidentiality.html
    # This should _never_ be production, and rarely any higher environments.
    replication_key_access_envs = ["dev"]

    # This is optional. If you'd like to receive notifications for configuration events, input a webhook url here.
    # You may enter it here, or instead update the vars/ files.
    slack_webhook_url = var.webhook_url

    # This is the alias for the account you will want custom figgy utilities to be installed. These utilities are not
    # specific to any environment. One example utility is the one-time-secret sharing mechanism provided by figgy.
    # The value here must match the value of `env_alias` in one of your vars/*.tfvars files.
    utility_account_alias = "mgmt"
  }
}