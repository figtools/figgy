from boto3.dynamodb.conditions import Key, Attr
from decimal import *
from figcli.config import *
from figcli.data.models.config_item import ConfigItem
from figcli.models.replication_config import ReplicationConfig, ReplicationType
from figcli.models.restore_config import RestoreConfig
from figcli.models.run_env import RunEnv
from figcli.models.audit_log import AuditLog
from figcli.models.parameter_history import ParameterHistory
from figcli.models.parameter_store_history import PSHistory
from typing import Callable, Dict, List, Any, Set
import json
import logging
import datetime
import time

log = logging.getLogger(__name__)


class ConfigDao:
    """
    This DAO executes queries against various DynamoDB tables required for our config management system's operation.
    1) Config replication table
    2) Audit Table
    3) Cache table.
    """

    def __init__(self, dynamo_resource):
        self._dynamo_resource = dynamo_resource
        self._config_repl_table = self._dynamo_resource.Table(REPL_TABLE_NAME)
        self._audit_table = self._dynamo_resource.Table(AUDIT_TABLE_NAME)
        self._cache_table = self._dynamo_resource.Table(CACHE_TABLE_NAME)

    def delete_config(self, destination: str, run_env: RunEnv) -> None:
        """
        Deletes a Replication configuration from the DB
        Args:
            destination: str -> /path/to/configuration/destination
            run_env: RunEnv -> run_env
        """
        self._config_repl_table.delete_item(
            Key={REPL_DEST_KEY_NAME: destination, REPL_RUN_ENV_KEY_NAME: run_env.env}
        )

    def get_parameter_restore_details(self, ps_name: str, start_key: str = None) -> List[RestoreConfig]:
        """
        :param ps_name:  str -> parameter store key name
        :param start_key: str -> used for recursive lookups on table scans.
        :return:
            List of parameter name + value + description + type
        """
        results = []
        filter_exp = Key(AUDIT_PARAMETER_KEY_NAME).eq(ps_name)
        if start_key:
            result = self._audit_table.scan(FilterExpression=filter_exp, ExclusiveStartKey=start_key)
        else:
            result = self._audit_table.scan(FilterExpression=filter_exp, )

        items: List = result["Items"] if result["Items"] else []

        # Remove items from list where action != "PutParameter"
        items = list(filter(lambda x: x["action"] == "PutParameter", items))

        results = sorted(RestoreConfig.convert_to_model(items), key=lambda x: x.ps_time, reverse=True)

        if 'LastEvaluatedKey' in result:
            results = results + self.get_parameter_restore_details(ps_name, start_key=result['LastEvaluatedKey'])

        # Convert to RestoreConfig model then sort list chronologically by timestamp
        return results

    def get_all_parameter_history(self, ps_time: datetime.datetime, ps_prefix: str, start_key=None) -> List[Dict]:
        """
        Scans in DynamoDb only do 1MB at at time. For large tables, we need to tell dynamo to KEEP_SCANNING. After each
        result set is returned, we need to inform dynamo to keep scanning to find ALL results across the full table. This
        will continue going back to dynamo until we find the _full_ history of a parameter.
        Args:
            ps_time: Time up to which parameter history should be returned.
            ps_prefix: e.g. /shared/some/prefix - Prefix to query under
            start_key: LastEvaluatedKey returned in scan results. Lets you konw if there is more scanning that can be done.
        Returns: List[Dict] of items returned from AWS API
        """
        time_end = Decimal(ps_time.timestamp() * 1000)
        filter_exp = Key(AUDIT_TIME_KEY_NAME).lt(time_end) & Key(AUDIT_PARAMETER_KEY_NAME).begins_with(ps_prefix)
        results = []

        if start_key:
            result = self._audit_table.scan(FilterExpression=filter_exp, ExclusiveStartKey=start_key)
        else:
            result = self._audit_table.scan(FilterExpression=filter_exp)

        if 'LastEvaluatedKey' in result:
            results.append(self.get_all_parameter_history(ps_time, ps_prefix, start_key=result['LastEvaluatedKey']))

        results.append(result)  # Add results from this query to list of lists

        results_list = list(map(lambda x: x['Items'], results))  # extract all the items
        result['Items'] = [item for sublist in results_list for item in sublist]  # Merge sublists to one list

        return result

    def get_parameter_history_before_time(self, ps_time: datetime.datetime, ps_prefix: str) -> PSHistory:
        """
        Retrieves total parameter history for all parameters up until the datetime passed in under the provided prefix.
        Args:
            ps_time: Time up to which parameter history should be returned.
            ps_prefix: e.g. /shared/some/prefix - Prefix to query under

        Returns:

        """

        result = self.get_all_parameter_history(ps_time, ps_prefix)
        items: List = result.get('Items', [])
        restore_cfgs: List[RestoreConfig] = RestoreConfig.convert_to_model(items)

        ps_histories: Dict[str, ParameterHistory] = {}
        for cfg in restore_cfgs:
            if ps_histories.get(cfg.ps_name, None):
                ps_histories.get(cfg.ps_name).add(cfg)
            else:
                ps_histories[cfg.ps_name] = ParameterHistory.instance(cfg)

        return PSHistory(list(ps_histories.values()))

    def get_parameter_restore_range(self, ps_time: datetime.datetime, ps_prefix: str, start_key: str = None) \
            -> List[RestoreConfig]:
        """
        :param ps_time:  int -> datetime to query dynamo timestamp from
        :param ps_prefix: str -> parameter store prefix we will recursively restore from/to (e.g., /app/demo-time)
        :return:
            List of parameter name + value + description + type for given time range
        """
        time_end = Decimal(ps_time.timestamp() * 1000)

        filter_exp = Key(AUDIT_TIME_KEY_NAME).lt(time_end) & Key(AUDIT_PARAMETER_KEY_NAME).begins_with(ps_prefix) \
                     & Attr(AUDIT_ACTION_ATTR_NAME).eq(SSM_PUT)

        if start_key:
            result = self._audit_table.scan(FilterExpression=filter_exp, ExclusiveStartKey=start_key)
        else:
            result = self._audit_table.scan(FilterExpression=filter_exp)

        items: List = result.get('Items', [])
        items = list(filter(lambda x: x["action"] == "PutParameter", items))

        return sorted(RestoreConfig.convert_to_model(items), key=lambda x: x.ps_time, reverse=True)

    def get_all_configs(self, run_env: RunEnv, namespace: str, start_key: str = None) -> List[ReplicationConfig]:
        """
        Retrieves all replication configs from the database for a particular namespace
        Args:
            start_key: LastEvaluatedKey returned in scan results. Lets you konw if there is more scanning that can be done.
            run_env: RunEnv -> run_env
            namespace: namespace  - e.g. /app/demo-time/

        Returns:
            List of ReplicationConfigs that match the namespace.

        """
        filter_exp = Attr(REPL_NAMESPACE_ATTR_NAME).eq(namespace) & Key(
            REPL_RUN_ENV_KEY_NAME
        ).eq(run_env.env)

        if start_key:
            result = self._config_repl_table.scan(FilterExpression=filter_exp, ExclusiveStartKey=start_key)
        else:
            result = self._config_repl_table.scan(FilterExpression=filter_exp)

        items = result["Items"] if result["Items"] else None

        configs = []
        if items is not None:
            for item in items:
                repl_config = ReplicationConfig(
                    item[REPL_DEST_KEY_NAME],
                    RunEnv(item[REPL_RUN_ENV_KEY_NAME]),
                    item[REPL_NAMESPACE_ATTR_NAME],
                    item[REPL_SOURCE_ATTR_NAME],
                    ReplicationType(item[REPL_TYPE_ATTR_NAME]),
                )
                configs.append(repl_config)

        if 'LastEvaluatedKey' in result:
            configs = configs + self.get_all_configs(run_env, namespace, start_key=result['LastEvaluatedKey'])

        return configs

    def get_cfgs_by_src(self, source: str, run_env: RunEnv) -> List[ReplicationConfig]:
        """
        Args:
            source: Source to perform table scan by
            run_env: RunEnv to query for.

        Returns: A list of matching replication confgs.
        """

        filter_exp = Attr(REPL_SOURCE_ATTR_NAME).eq(source) & Key(
            REPL_RUN_ENV_KEY_NAME
        ).eq(run_env.env)
        result = self._config_repl_table.scan(FilterExpression=filter_exp)
        return self._map_results(result)

    def get_config_repl(self, destination: str, run_env: RunEnv) -> ReplicationConfig:
        """
        Lookup a replication config by destination / run_env
        Args:
            destination: str: /app/demo-time/replicated/destination/path
            run_env: RunEnvironment -> run_env

        Returns: Matching replication config, or None if none match.
        """

        filter_exp = Key(REPL_DEST_KEY_NAME).eq(destination) & Key(
            REPL_RUN_ENV_KEY_NAME
        ).eq(run_env.env)
        result = self._config_repl_table.query(KeyConditionExpression=filter_exp)

        if "Items" in result and len(result["Items"]) > 0:
            items = result["Items"][0]

            config = ReplicationConfig(
                items[REPL_DEST_KEY_NAME],
                RunEnv(items[REPL_RUN_ENV_KEY_NAME]),
                items[REPL_NAMESPACE_ATTR_NAME],
                items[REPL_SOURCE_ATTR_NAME],
                ReplicationType(items[REPL_TYPE_ATTR_NAME]),
                user=items[REPL_USER_ATTR_NAME],
            )
            return config
        else:
            return None

    def put_config_repl(self, config: ReplicationConfig) -> None:
        """
        Stores a replication configuration
        Args:
            config: ReplicationConfig -> a hydrated replication config object.
        """
        item = {
            REPL_DEST_KEY_NAME: config.destination,
            REPL_RUN_ENV_KEY_NAME: config.run_env,
        }

        for key in config.props:
            if (
                    key != REPL_DEST_KEY_NAME
                    and key != REPL_RUN_ENV_KEY_NAME
                    and not isinstance(config.props[key], float)
            ):
                item[key] = config.props[key]
            elif isinstance(config.props[key], float):
                item[key] = Decimal(f"{config.props[key]}")

        self._config_repl_table.put_item(Item=item)

    def _map_results(self, result: dict) -> List[ReplicationConfig]:
        """
        Takes a DDB Result object with a single result and maps it into a replication config
        Args:
            result: DDB boto3 result obj

        Returns: ReplicationConfig if result is found, else and empty list

        """
        repl_cfgs = []
        if "Items" in result and len(result["Items"]) > 0:
            for item in result["Items"]:
                config = ReplicationConfig(
                    item[REPL_DEST_KEY_NAME],
                    RunEnv(item[REPL_RUN_ENV_KEY_NAME]),
                    item[REPL_NAMESPACE_ATTR_NAME],
                    item[REPL_SOURCE_ATTR_NAME],
                    ReplicationType(item[REPL_TYPE_ATTR_NAME]),
                    user=item[REPL_USER_ATTR_NAME],
                )
                repl_cfgs.append(config)

        return repl_cfgs

    def get_audit_logs(self, ps_name: str) -> List[AuditLog]:
        """
        Args:
            ps_name: /path/to/parameter to query audit logs for.

        Returns: List[AuditLog]. Logs that match for the /ps/name in ParameterStore.
        """
        filter_exp = Key(AUDIT_PARAMETER_KEY_NAME).eq(ps_name)
        result = self._audit_table.query(KeyConditionExpression=filter_exp)
        items = result.get('Items', None)

        audit_logs: List[AuditLog] = []
        if items is not None:
            for item in items:
                log = AuditLog(item[AUDIT_PARAMETER_KEY_NAME], item[AUDIT_TIME_KEY_NAME],
                               item[AUDIT_ACTION_ATTR_NAME], item[AUDIT_USER_ATTR_NAME])
                audit_logs.append(log)

        return audit_logs

    def get_all_config_names(self, prefix: str = None, one_level: bool = False, start_key: str = None) -> Set[str]:
        """
        Retrieve all key names from the Dynamo DB config-cache table in each account. Much more efficient than
        querying SSM directly.
        Args:
            start_key: Optional: Is used for recursive paginated lookups to get the full data set. This should not
            be passed in by the user.
        Returns:

        """
        start_time = time.time()
        if start_key:
            log.info(f"Recursively scanning with start key: {start_key}")
            result = self._cache_table.scan(ExclusiveStartKey=start_key)
        else:
            result = self._cache_table.scan()

        configs: Set[str] = set()
        if "Items" in result and len(result['Items']) > 0:
            for item in result['Items']:
                name = item[CACHE_PARAMETER_KEY_NAME]
                configs.add(name)

        if prefix:
            configs = set(filter(lambda x: x.startswith(prefix), configs))

        if one_level:
            configs = set(filter(lambda x: len(x.split('/')) == len(prefix.split('/')) + 1, configs))

        if 'LastEvaluatedKey' in result:
            configs = configs | self.get_all_config_names(prefix, one_level, start_key=result['LastEvaluatedKey'])

        log.info(
            f"Returning config names from dynamo cache after: {time.time() - start_time} "
            f"seconds with {len(configs)} configs.")
        return configs

    def get_config_names_after(self, millis_since_epoch: int) -> Set[ConfigItem]:
        """
        Retrieve all key names from the Dynamo DB config-cache table in each account. Much more efficient than
        querying SSM directly.
        Args:
            millis_since_epoch: milliseconds in epoch to lookup config names from cache after
        Returns: Set[str] -> configs that have been added to cache table after millis_since_epoch
        """

        request = {
            'attribute_names': {
                '#n1': CACHE_LAST_UPDATED_KEY_NAME
            },
            'attribute_values': {
                ':v1': {'N': millis_since_epoch}
            },
            'expression': Attr(CACHE_LAST_UPDATED_KEY_NAME).gt(millis_since_epoch)
        }

        start_time = time.time()
        response = self._cache_table.scan(
            FilterExpression=request['expression']
        )

        items = response.get('Items', [])

        while 'LastEvaluatedKey' in response:
            response = self._cache_table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items = items + response.get('Items', [])

        configs: Set[ConfigItem] = set()
        for item in items:
            configs.add(ConfigItem.from_dict(item))

        log.info(f"Returning {len(configs)} parameter names from dynamo cache after time: [{millis_since_epoch}] in "
                 f"{time.time() - start_time} seconds.")

        return configs

    def put_in_config_cache(self, name):
        item = {
            CACHE_PARAMETER_KEY_NAME: name
        }

        self._cache_table.put_item(Item=item)
