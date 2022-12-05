variable "lambda_name" {
  description = "Name of lambda to apply event trigger to"
}

variable "lambda_arn" {
  description = "ARN of lambda to trigger from the S3 events."
}

variable "bucket_name" {
  description = "Name of bucket to generate create notification triggers on."
}

variable "s3_event_types" {
  type = list(string)
  description = "S3 event type to generate event off of. i.e. `s3:ObjectCreated` https://docs.aws.amazon.com/AmazonS3/latest/dev/NotificationHowTo.html#supported-notification-event-types"
}

variable "filter_prefix" {
  description = "Prefix of S3 Key names to be filterd on. I.E. `images/`"
}

variable "filter_suffix" {
  description = "Suffix of S3 Key to be filtered on I.E. `.jpg`"
}