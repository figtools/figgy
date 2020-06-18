from figcli.models.run_env import RunEnv
from figcli.config import *
import getpass
from typing import Dict, List
from figcli.utils.utils import *


class ReplicationType:
    """
    Represents the various types of replication configs that are valid for storing into our dynamodb
    `service-config-replication` table
    """

    def __init__(self, type: str):
        assert type in repl_types, f"Type: {type} must be one of: {repl_types}"
        self.type = type


class ReplicationConfig:
    """
    This model is used for storing / retrieving data from the `service-config-replication` table.
    """

    def __init__(self, destination: str, run_env: RunEnv, namespace: str, source: str, type: ReplicationType,
                 user: str = None):
        self.destination = destination
        self.run_env = run_env.env
        self.namespace = namespace
        self.source = source
        self.type = type.type
        self.user = user

        if user is None:
            self.user = getpass.getuser()

        self.props = {
            REPL_SOURCE_ATTR_NAME: self.source,
            REPL_NAMESPACE_ATTR_NAME: self.namespace,
            REPL_TYPE_ATTR_NAME: self.type,
            REPL_USER_ATTR_NAME: self.user
        }

    @staticmethod
    def from_dict(conf: Dict, type: ReplicationType, run_env: RunEnv,
                  namespace: str = None, user: str = None) -> List:
        """
        Dict must be of format - Key (source) -> Value (destination)
        Args:
            conf: Key (repl source) -> Value (repl dest) dictionary
            type: required - Type of replication config (merge / app)
            run_env: RunEnvironment, optional
            namespace: Dest App Namespace, optional
            user: User who is creating this REPL Conf, also optional
        Returns:
            List[ReplicationConfig] - List of hydrated replication config objects based on the parameters.
        """
        cfgs = []
        for key in conf:
            if namespace is None:
                namespace = Utils.parse_namespace(conf[key])
            if user is None:
                user = getpass.getuser()
            cfgs.append(ReplicationConfig(destination=conf[key], source=key, type=type,
                                          run_env=run_env, namespace=namespace, user=user))
        return cfgs

    def __str__(self):
        return f"{self.__dict__}"

    def __hash__(self):
        return hash(f"{self.destination}{self.source}{self.type}")

    def __eq__(self, other):
        if isinstance(other, ReplicationConfig):
            return self.destination == other.destination and self.source == other.source and self.type == other.type
        return False
