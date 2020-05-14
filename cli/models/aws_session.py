from dataclasses import dataclass
from typing import Dict


# Todo add support for expiration and check for expiration rather than calling STS with session.
@dataclass
class FiggyAWSSession:
    access_key: str
    secret_key: str
    token: str

    @staticmethod
    def from_sts_response(response: Dict) -> "FiggyAWSSession":
        creds = response.get('Credentials', {})

        return FiggyAWSSession(
            access_key=creds.get('AccessKeyId'),
            secret_key=creds.get('SecretAccessKey'),
            token=creds.get('SessionToken')
        )


"""
Example STS boto response:

{
    'Credentials': {
        'AccessKeyId': 'string',
        'SecretAccessKey': 'string',
        'SessionToken': 'string',
        'Expiration': datetime(2015, 1, 1)
    },
    'AssumedRoleUser': {
        'AssumedRoleId': 'string',
        'Arn': 'string'
    },
    'PackedPolicySize': 123
}
"""
