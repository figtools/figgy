# This is optional, you may also select an existing bucket, feel free to comment out.
# If you comment this out, ensure your bucket exists, and then comment out delete the `depends_on` blocks  referencing
# `aws_s3_bucket.figgy_bucket` in the files prefixed with `lambda_`
resource "aws_s3_bucket" "figgy_bucket" {
  count = local.custom_bucket == true ? 0 : 1
  bucket = var.deploy_bucket
  acl    = "private"

  versioning {
    enabled = true
  }

  tags = {
    Name        = "figgy"
    run_env     = var.run_env
    created_by  = "figgy"
  }
}

locals {
  lambda_bucket_id = local.custom_bucket == true ? var.deploy_bucket : aws_s3_bucket.figgy_bucket[0].id
}