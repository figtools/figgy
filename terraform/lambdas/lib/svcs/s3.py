class S3Service:

    def __init__(self, s3_client):
        self._s3 = s3_client  # initialized hydrated boto3 s3 client.

    def download_file(self, bucket: str, obj_key: str, download_destination: str) -> None:
        with open(download_destination, 'wb') as f:
            self._s3.download_fileobj(bucket, obj_key, f)
