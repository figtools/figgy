resource "random_uuid" "uuid" {}

locals {
  bucket_name = "${var.cfgs.s3_bucket_prefix}figgy-${substr(random_uuid.uuid.result, 10)}"
}

# This is optional, you may also select an existing bucket, feel free to comment out.
# If you comment this out, ensure your bucket exists, and then comment out delete the `depends_on` blocks  referencing
# `aws_s3_bucket.figgy_bucket` in the files prefixed with `lambda_`
resource "aws_s3_bucket" "figgy_bucket" {
  bucket = var.deploy_bucket
  acl    = "private"

  versioning {
    enabled = true
  }

  tags = {
    Name       = "figgy"
    env_alias    = var.env_alias
    created_by = "figgy"
  }

  lifecycle_rule {
    enabled = false

    # Cloudtrail logs should be auto-expired after 1 day, we don't need to keep them, they ain't our business!
    expiration {
      days = 1
    }
  }

  provisioner "local-exec" {
    command = "echo \"Sleeping for 15s to address potential race condition\" && sleep 15"
  }
}

# You will need this if you do **_NOT_** already have cloud-trail logging events
# Generally I would not recommend using figgy to manage your cloudtrail, but this will ensure your events are properly
# capture and figgy can use them for its event-driven config workflow :)
resource "aws_s3_bucket_policy" "cloudtrail_bucket_policy" {
  count  = var.cfgs.create_deploy_bucket == true && var.cfgs.configure_cloudtrail ? 1 : 0
  bucket = var.deploy_bucket
  depends_on = [aws_s3_bucket.figgy_bucket]
  policy = <<POLICY
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "AWSCloudTrailAclCheck",
            "Effect": "Allow",
            "Principal": {
              "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "s3:GetBucketAcl",
            "Resource": "arn:aws:s3:::${var.deploy_bucket}"
        },
        {
            "Sid": "AWSCloudTrailWrite",
            "Effect": "Allow",
            "Principal": {
              "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::${var.deploy_bucket}/AWSLogs/*",
            "Condition": {
                "StringEquals": {
                    "s3:x-amz-acl": "bucket-owner-full-control"
                }
            }
        }
    ]
}
POLICY
}

