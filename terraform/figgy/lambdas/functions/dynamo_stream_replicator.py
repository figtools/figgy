from config.constants import *
from lib.models.replication_config import ReplicationConfig
from lib.init.repl_init import *


def handle(event, context):
    lazy_init()

    print(f"Got Event: {event} with context {context}")

    records = event.get('Records', [])
    for record in records:
        event_name = record.get("eventName")
        # Only resync on adds / updates, never on deletes.
        if event_name != 'REMOVE':
            ddb_record = record.get("dynamodb", {})
            keys = ddb_record.get("Keys", {})
            destination = keys.get(REPL_DEST_KEY_NAME, {}).get("S", None)
            run_env = keys.get(REPL_RUN_ENV_KEY_NAME, {}).get("S", None)
            if destination and run_env:
                print(f"Record updated with key: {destination} and run_env: {run_env}")
                config: ReplicationConfig = repl_dao.get_config_repl(destination, run_env)
                print(f"Got config: {config}, syncing...")
                repl_svc.sync_config(config)
        else:
            print("Event is a delete event, skipping!")


if __name__ == '__main__':
    handle(None, None)
