data "archive_file" "figgy" {
  source_dir  = "lambdas/"
  output_path = "figgy.zip"
  type        = "zip"
  depends_on = [time_sleep.wait_45_seconds]
}

# Required to work around race condition for users creating their own S3 bucket. Traditional depedency mapping
# does not work with data sources in this situation
resource "time_sleep" "wait_45_seconds" {
  create_duration = "45s"
}