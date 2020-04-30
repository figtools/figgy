from config import *
from typing import List


class ServiceStateDao:
    def __init__(self, dynamo_resource):
        self._dynamo_resource = dynamo_resource
        self._service_state_table = self._dynamo_resource.Table(SERVICE_STATE_TABLE_NAME)

    def get_cve_overrides(self, service_name) -> List[str]:
        """
        Returns a list of CVE overrides for a particular service.
        Args:
            service_name: Service to query overrides for.

        Returns: List[str] - List of current CVE overrides.
        """

        result = self._service_state_table.get_item(
            Key={
                SERVICE_STATE_KEY_NAME: service_name
            }
        )

        result = result.get('Item', {}).get(SERVICE_STATE_CVE_ATTR_NAME, None)
        if result:
            return result.split(',')
        else:
            return []

    def override_cve(self, service_name: str, cve: str):
        """
        Updates a plugin's sha1 in the plugin-state table, which in turn "validates" it.
        Args:
            service_name: service_name as defined in locals.tf
            cve: cve to override for service
        """

        cve_list = self.get_cve_overrides(service_name)
        cve_list.append(cve)

        self._service_state_table.update_item(
            Key={
                SERVICE_STATE_KEY_NAME: service_name
            },
            UpdateExpression=f"SET {SERVICE_STATE_CVE_ATTR_NAME}=:cv",
            ExpressionAttributeValues={
                ":cv": ','.join(cve_list)
            }
        )
