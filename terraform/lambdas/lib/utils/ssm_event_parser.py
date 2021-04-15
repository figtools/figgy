import time
import logging

from typing import Dict, List
from datetime import datetime

from config.constants import PUT_PARAM_ACTION

log = logging.getLogger(__name__)


class SSMErrorDetected(Exception):
    pass


class SSMEvent:
    detail: Dict
    user: str
    user_arn: str
    action: str
    parameters: List[str]
    time: int
    error_message: str
    error_code: str
    request_params: Dict
    value: str
    type: str
    description: str
    version: int
    key_id: str
    name: str

    def __init__(self, event: Dict):
        self.event: Dict = event
        self.detail = event["detail"]
        self.validate()

        self.user_arn = self.detail.get("userIdentity", {}).get("arn", "UserArnUnknown")
        self.user = self.user_arn.split("/")[-1:][0]
        self.action = self.detail.get("eventName")
        self.request_params = self.detail.get('requestParameters', {})
        self.version = self.detail.get("responseElements", {}).get("version", 1)

        ps_names = self.request_params.get('names', [])
        ps_name = [self.request_params['name']] if 'name' in self.request_params else []
        self.parameters = ps_names + ps_name
        event_time = self.detail.get('eventTime')

        # Convert to millis since epoch
        if event_time:
            self.time = int(datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%SZ").timestamp() * 1000)
        else:
            self.time = int(time.time() * 1000)

        if self.action == PUT_PARAM_ACTION:
            self.value = self.request_params.get("value")
            self.type = self.request_params.get("type")
            self.description = self.request_params.get("description")
            self.version = self.version
            self.key_id = self.request_params.get("keyId")

    def validate(self):
        throw = False
        if 'errorMessage' in self.detail:
            self.error_message = self.detail['errorMessage']
            throw = True
        elif 'errorCode' in self.detail:
            self.error_code = self.detail['errorCode']
            throw = True

        if throw:
            raise SSMErrorDetected("Detected errorMessage in event details")
