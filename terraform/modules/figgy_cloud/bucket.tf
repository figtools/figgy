resource "random_uuid" "uuid" {}

locals {
  bucket_name = "${var.cfgs.s3_bucket_prefix}figgy-${substr(random_uuid.uuid.result, 0, 5)}"
}

# This is optional, you may also select an existing bucket, feel free to comment out.
# If you comment this out, ensure your bucket exists, and then comment out delete the `depends_on` blocks  referencing
# `aws_s3_bucket.figgy_bucket` in the files prefixed with `lambda_`
resource "aws_s3_bucket" "figgy_bucket" {
  count = var.primary_region ? 1 : 0
  bucket = local.bucket_name
  acl    = "private"

  versioning {
    enabled = false
  }

  tags = {
    Name       = "figgy"
    env_alias    = var.env_alias
    created_by = "figgy"
  }


  # Cloudtrail logs should be auto-expired after 1 day. If we avoid writing to S3 altogether we would.
  lifecycle_rule {
    enabled = true
    prefix = "AWSLogs/"

    expiration {
      days = 1
    }
  }

  provisioner "local-exec" {
    command = "echo \"Sleeping for 15s to address potential race condition\" && sleep 15"
  }
}

resource "aws_s3_bucket_policy" "cloudtrail_bucket_policy" {
  bucket = aws_s3_bucket.figgy_bucket.id
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
            "Resource": "arn:aws:s3:::${aws_s3_bucket.figgy_bucket.id}"
        },
        {
            "Sid": "AWSCloudTrailWrite",
            "Effect": "Allow",
            "Principal": {
              "Service": "cloudtrail.amazonaws.com"
            },
            "Action": "s3:PutObject",
            "Resource": "arn:aws:s3:::${aws_s3_bucket.figgy_bucket.id}/AWSLogs/*",
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

