data "aws_s3_bucket" "deploy_bucket" {
  bucket = var.deploy_bucket
}


### This is optional, you may also select an existing bucket, feel free to comment out.
resource "aws_s3_bucket" "figgy_bucket" {
  bucket = var.deploy_bucket
  acl    = "private"

  versioning {
    enabled = true
  }

  tags = {
    Name        = "figgy"
    run_env      = var.run_env
  }
}