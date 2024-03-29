## This Multi Environment terraform project contains app specific iam policies / roles that will be used
## across multiple different apps and multiple environments. For roles / policies specific to a single application,
## include it in the app configuration itself.

# TODO: You must configure this to point the appropriate backend of your choosing.
# TODO: You may use S3 / Terraform Cloud (recommended) / Local / etc.
# TODO: Docs: https://www.terraform.io/docs/backends/index.html
terraform {
  required_version = ">=0.15.0"

  backend "remote" {
    hostname = "app.terraform.io"
    organization = "your-org"

    workspaces {
      prefix = "figgy-"
    }
  }

  required_providers {
    aws = {
      source = "hashicorp/aws"
      version = "~>3.0"
    }
  }
}

# TODO: You will need to configure this to point to YOUR environment. Use profiles, role assumption, whatever makes
# TODO: sense for your terraform environment. Docs: https://www.terraform.io/docs/providers/aws/index.html
provider "aws" {
  region = "us-east-1"

  assume_role {
    ## Todo: Update this to your own role, or remove this block and provide credentials to
    ## Todo: Terraform some other way.
    role_arn     = "arn:aws:iam::${var.aws_account_id}:role/figgy-admin"
  }
}

############################################
### MULTI REGION DEPLOYMENT CONFIG BELOW ###
############################################

# Comment out the below block (and duplicate if necessary) if you intend to run Figgy across multiple regions.
# Unfortunately terraform does not yet support count() inside of the provider blocks so
# You will need to create N provider blocks for the N regions as defined in your var.regions
# variable -- hint, it's in your vars/*.tfvars files ;).

//provider "aws" {
//  region = "us-west-1"
//  alias = "usw1"
//
//  assume_role {
//    ## Todo: Update this to your own role, or remove this block and provide credentials to
//    ## Terraform some other way.
//    role_arn     = "arn:aws:iam::${var.aws_account_id}:role/figgy-admin"
//  }
//}


