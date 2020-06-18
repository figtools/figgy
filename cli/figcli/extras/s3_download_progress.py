import urllib, os
from tqdm import tqdm


class S3Progress(tqdm):

    def __call__(self, downloaded_bytes):
        self.update(downloaded_bytes)
