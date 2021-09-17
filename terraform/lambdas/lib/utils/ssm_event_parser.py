import time
import logging

from typing import Dict, List
from datetime import datetime

from lib.config.constants import PUT_PARAM_ACTION

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
        log.info(f'Parsing event: {event}')
        self.event = event
        self.error_message = self.event.get('errorMessage')
        self.error_code = self.event.get('errorCode')
        self.user_arn = self.event.get("userIdentity", {}).get("arn", "UserArnUnknown")
        self.user = self.user_arn.split("/")[-1:][0]
        self.action = self.event.get("eventName")
        self.request_params = self.event.get('requestParameters', {})
        self.response_elements = self.event.get("responseElements", {})

        ps_names = self.request_params.get('names', [])
        ps_name = [self.request_params['name']] if 'name' in self.request_params else []
        self.parameters = ps_names + ps_name
        event_time = self.event.get('eventTime')

        if self.response_elements:
            log.info(f'Got response elements, getting version')
            self.version = self.response_elements.get("version", 1)

        # Convert to millis since epoch
        if event_time:
            self.time = int(datetime.strptime(event_time, "%Y-%m-%dT%H:%M:%SZ").timestamp() * 1000)
        else:
            self.time = int(time.time() * 1000)

        if self.action == PUT_PARAM_ACTION:
            self.value = self.request_params.get("value")
            self.type = self.request_params.get("type")
            self.description = self.request_params.get("description")
            self.key_id = self.request_params.get("keyId")

    def is_error(self):
        return self.error_code or self.error_message
