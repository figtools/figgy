from figcli.data.dao.ssm import SsmDao
from botocore.exceptions import ClientError
import botocore.session
from typing import Dict
from figcli.utils.utils import Utils


class SSMRebirth:
    def __init__(self):
        aws_session = botocore.session.get_session()
        boto_client = aws_session.create_client("ssm", "us-east-1")
        self._ssm: SsmDao = SsmDao(boto_client)
        self._utils = Utils(True)

    def _client_exception_msg(self, item: Dict, e: ClientError):
        if "AccessDeniedException" == e.response["Error"]["Code"]:
            print(
                f"\n\nYou do not have permissions to a new config value at the path: "
                f"{item['parameter_name']}"
            )
        else:
            print(f"Error message: {e.response['Error']['Message']}")

    def start(self):
        items = self._ssm.get_all_parameters("/")

        for item in items:

            try:
                key_id = None if item["Type"] == "String" else item["KeyId"]

                # Grab decrypted value from SSM for key
                value = self._ssm.get_parameter(item["Name"])
                print(f"Key {item['Name']} has value: {value}")

                description = item["Description"] if "Description" in item else ""

                # Test to make sure we can write to this parameter path
                # If this fails, an exception should be thrown.
                self._ssm.set_parameter(
                    item["Name"],
                    value,
                    description,
                    item["Type"],
                    key_id,
                )

                print(f"Deleting: {item['Name']}")
                self._ssm.delete_parameter(item["Name"])

                print(f"Recreating: {item['Name']}")
                self._ssm.set_parameter(
                    item["Name"],
                    value,
                    description,
                    item["Type"],
                    key_id,
                )

            except ClientError as e:
                self._client_exception_msg(item, e)


if __name__ == "__main__":
    rebirth = SSMRebirth()
    rebirth.start()
