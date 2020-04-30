from typing import List

from config.constants import *
from lib.models.replication_config import ReplicationType, ReplicationConfig
from lib.init.repl_init import *


def handle(event, context):
    lazy_init()
    print(f"Event: {event}")
    detail = event["detail"]
    action = detail["eventName"]

    if 'errorMessage' in detail:
        print(f'Not processing event due to this being an error event with message: {detail["errorMessage"]}')
        return

    ps_name = detail.get('requestParameters', {}).get('name')

    if ps_name and action == PUT_PARAM_ACTION:
        repl_configs: List[ReplicationConfig] = repl_dao.get_config_repl_by_source(ps_name)
        merge_configs: List[ReplicationConfig] = repl_dao.get_configs_by_type(ReplicationType(REPL_TYPE_MERGE))
        for config in repl_configs:
            repl_svc.sync_config(config)

        for config in merge_configs:
            print(f"Evaluating config: {config}")
            if isinstance(config.source, list):
                for source in config.source:
                    if ps_name in source:
                        repl_svc.sync_config(config)
                        continue
    elif action == DELETE_PARAM_ACTION or action == DELETE_PARAMS_ACTION:
        print("Delete found, skipping...")
    else:
        print(f"Unsupported action type found! --> {action}")


if __name__ == '__main__':
    handle(None, None)
