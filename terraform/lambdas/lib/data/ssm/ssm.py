from botocore.exceptions import ClientError
from typing import Dict, List, Set, Union

from lib.utils.utils import Utils

SSM_SECURE_STRING = "SecureString"


class SsmDao:
    def __init__(self, boto_ssm_client):
        self._ssm = boto_ssm_client

    @Utils.retry_on_throttle
    def get_all_param_names(self, prefixes: List[str], option: str = 'Recursive', page: str = None) -> Set[str]:
        params = self.get_all_parameters(prefixes, option, page)
        return set([param['Name'] for param in params])

    @Utils.retry_on_throttle
    def get_all_parameters(self, prefixes: List[str], option: str = 'Recursive', page: str = None) -> List[dict]:
        """
        Returns all parameters under prefix. Automatically pages recursively then returns full result set
        Args:
            prefixes: List of prefixes to query. E.G. [ '/shared', '/data', '/app' ]
            existing_params: Used in recursive calls to build a total result set
            page: Used in recursive calls if more pages exist.
            option: Must be 'Recursive' or 'OneLevel' - Indiates # of levels below the prefix to recurse.
        Returns: List[dict] -> Parameter details as returned from AWS API
        """
        filters = {
                      'Key': 'Path',
                      'Option': f'{option}',
                      'Values': prefixes
                  },
        total_params = []
        if page:
            params = self._ssm.describe_parameters(ParameterFilters=filters, NextToken=page,
                                                   MaxResults=50)
        else:
            params = self._ssm.describe_parameters(ParameterFilters=filters, MaxResults=50)

        total_params = total_params + params['Parameters']

        if params and 'NextToken' in params:
            total_params = total_params + self.get_all_parameters(prefixes, option=option, page=params['NextToken'])

        return total_params

    @Utils.retry_on_throttle
    def delete_parameter(self, key) -> None:
        response = self._ssm.delete_parameter(Name=key)
        assert response and response['ResponseMetadata'] and response['ResponseMetadata']['HTTPStatusCode'] \
               and response['ResponseMetadata']['HTTPStatusCode'] == 200, \
            f"Error deleting key: [{key}] from PS. Please try again."

    @Utils.retry_on_throttle
    def get_parameter(self, key) -> Dict:
        try:
            return self._ssm.get_parameter(Name=key, WithDecryption=True)
        except ClientError:
            return None

    @Utils.retry_on_throttle
    def get_parameter_value(self, key) -> Union[str, None]:
        try:
            parameter = self._ssm.get_parameter(Name=key, WithDecryption=True)
            return parameter.get('Parameter', {}).get('Value')
        except ClientError as e:
            if "ParameterNotFound" == e.response['Error']['Code']:
                return None
            else:
                raise

    @Utils.retry_on_throttle
    def get_parameter_value_encrypted(self, key) -> Union[str, None]:
        """
            Returns the parameter without decrypting the value. If parameter isn't encrypted, it returns the value.
        Args:
            key: The PS Name - E.G. /app/demo-time/parameter/abc123

        Returns: str -> encrypted string value of an encrypted parameter.

        """
        try:
            parameter = self._ssm.get_parameter(Name=key, WithDecryption=False)
            return parameter.get('Parameter', {}).get('Value')
        except ClientError as e:
            if "ParameterNotFound" == e.response['Error']['Code']:
                return None
            else:
                raise

    @Utils.retry_on_throttle
    def set_parameter(self, key, value, desc, type, key_id=None) -> None:
        if key_id and type == SSM_SECURE_STRING:
            self._ssm.put_parameter(
                Name=key,
                Description=desc,
                Value=value,
                Overwrite=True,
                Type=type,
                KeyId=key_id
            )
        else:
            self._ssm.put_parameter(
                Name=key,
                Description=desc,
                Value=value,
                Overwrite=True,
                Type=type
            )
