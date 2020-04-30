## Please fill out this file to custom-configure your figgy deployment to meet your needs

locals {
  # If you don't want figgy to create its own S3 bucket, set this to true, then specify the `var.deploy_bucket` variable.
  custom_bucket = false



}