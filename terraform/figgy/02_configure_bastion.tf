# THIS IS OPTIONAL. Only configure this if you are using bastion-account-based authentication and _not_ SSO authentication.

locals {
  # Please provide a mapping from all AWS "environments" to their respective account Ids
  # Format: "env" -> "account_id"
  associated_accounts = tomap({
    "dev" : "106481321259",
    "qa" :  "713117490776",
    "stage": "750075891372",
    "prod" : "816636370623",
    "bastion" : "816219277933"
  })

  # Here, do a mapping of each user and their specified role(s)
  # These will be dynamically provisioned and configured for cross-account role authorizations
  bastion_users = tomap({
    "jordan.devops": ["devops", "dev", "dba", "sre", "data"]
    "jordan.dba": ["dba"]
    "jordan.sre": ["sre"]
    "jordan.data": ["dba", "data"]
    "jordan.dev": ["dev"]
  })
}


