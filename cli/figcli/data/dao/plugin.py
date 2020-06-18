from figcli.config import *


class PluginDao:
    def __init__(self, dynamo_resource):
        self._dynamo_resource = dynamo_resource
        self._plugin_table = self._dynamo_resource.Table(PLUGIN_TABLE_NAME)

    def validate(self, service_name: str, plugin_name: str, sha1: str, user: str):
        """
        Updates a plugin's sha1 in the plugin-state table, which in turn "validates" it.
        Args:
            service_name: service_name as defined in locals.tf
            plugin_name: plugin_name to validate as defined in figgy.json
            sha1: sha1 that is printed as part of the build output
            user: User performing the validation. Needed for change tracking purposes.
        """
        self._plugin_table.update_item(
            Key={
                PLUGIN_SERVICE_KEY_NAME: service_name,
                PLUGIN_PLUGIN_KEY_NAME: plugin_name
            },
            UpdateExpression=f"SET {PLUGIN_SHA_ATTR_NAME}=:sh, {PLUGIN_USER_ATTR_NAME}=:us",
            ExpressionAttributeValues={
                ":sh": sha1,
                ":us": user
            }
        )
