import re
import logging
import sys
import time
import traceback
from functools import wraps

from botocore.exceptions import ClientError

log = logging.getLogger(__name__)


class Utils:
    @staticmethod
    def parse_namespace(app_key: str) -> str:
        get_ns = re.compile(r"^(/app/[A-Za-z0-9_-]+/).*")
        val = get_ns.match(app_key)
        return val.group(1)

    @staticmethod
    def validate(bool, error_msg):
        if not bool:
            raise ValueError(error_msg)

    @staticmethod
    def get_logger(name, log_level):
        root_logger = logging.getLogger()
        root_logger.setLevel(log_level)

        return logging.getLogger(name)

    @staticmethod
    def printable_exception(e: Exception):
        printable_exception = ''.join(traceback.format_exception(etype=type(e), value=e, tb=e.__traceback__))
        return printable_exception

    @staticmethod
    def retry_on_throttle(f):
        @wraps(f)
        def wrapped_f(*args, **kwargs):
            backoff = .25
            while True:
                try:
                    return f(*args, **kwargs)
                except ClientError as e:
                    if "ThrottlingException" == e.response['Error']['Code']:
                        log.info(f'Caught throttling exception. Backing off by {backoff} seconds')
                        time.sleep(backoff)
                        backoff = backoff * 1.5
                        continue
                    else:
                        raise

        return wrapped_f
