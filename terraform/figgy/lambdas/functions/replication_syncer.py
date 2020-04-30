import time

from lib.init.repl_init import *


def handle(event, context):
    lazy_init()

    repl_configs = repl_dao.get_all()
    for config in repl_configs:
        repl_svc.sync_config(config)
        time.sleep(.15)  # This is to throttle PS API Calls to prevent overloading the API.


if __name__ == '__main__':
    handle(None, None)
