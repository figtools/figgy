from figcli.models.run_env import RunEnv
from figcli.config import *
import getpass
from decimal import Decimal
from typing import List, Dict, TypeVar
import datetime

T = TypeVar('T', bound='RestoreConfig')


class RestoreConfig:
    """
    Model used for defining values used to restore a parameter from parameter store
    """

    def __init__(
            self,
            ps_description: str,
            ps_name: str,
            ps_time: Decimal,
            ps_type: str,
            ps_key_id: str,
            ps_value: str,
            ps_version: str,
            ps_user: str,
            ps_action: str,
    ):
        self.ps_type = ps_type
        self.ps_key_id = ps_key_id
        self.ps_time = ps_time
        self.ps_description = ps_description
        self.ps_value = ps_value
        self.ps_name = ps_name
        self.ps_version = ps_version
        self.ps_user = ps_user
        self.ps_action = ps_action

        self.props = {
            AUDIT_PARAMETER_ATTR_DESCRIPTION: self.ps_description,
            AUDIT_PARAMETER_KEY_NAME: self.ps_name,
            AUDIT_TIME_KEY_NAME: self.ps_time,
            AUDIT_PARAMETER_ATTR_TYPE: self.ps_type,
            AUDIT_PARAMETER_ATTR_KEY_ID: self.ps_key_id,
            AUDIT_PARAMETER_ATTR_VALUE: self.ps_value,
            AUDIT_PARAMETER_ATTR_VERSION: self.ps_version,
            AUDIT_USER_ATTR_NAME: self.ps_user,
            AUDIT_ACTION_ATTR_NAME: self.ps_action
        }

    @staticmethod
    def convert_to_model(items: List[Dict]) -> List[T]:
        models: List[RestoreConfig] = []

        for item in items:
            model = RestoreConfig(
                item.get(AUDIT_PARAMETER_ATTR_DESCRIPTION, ""),
                item[AUDIT_PARAMETER_KEY_NAME],
                item[AUDIT_TIME_KEY_NAME],
                item.get(AUDIT_PARAMETER_ATTR_TYPE, ""),
                item.get(AUDIT_PARAMETER_ATTR_KEY_ID, None),
                item.get(AUDIT_PARAMETER_ATTR_VALUE, ""),
                item.get(AUDIT_PARAMETER_ATTR_VERSION, ""),
                item.get(AUDIT_USER_ATTR_NAME, ""),
                item[AUDIT_ACTION_ATTR_NAME]
            )

            models.append(model)

        return models

    def __str__(self) -> str:
        return f"{self.__dict__}"
