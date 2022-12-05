import gzip
import json
from typing import Dict, Iterable

from lib.utils.ssm_event_parser import SSMEvent

SSM_PRINCIPAL = 'ssm.amazonaws.com'


class CloudtrailParser:
    _gzip_path: str

    def __init__(self, cloudtrail_file_path: str):
        self._gzip_path = cloudtrail_file_path

    def parse(self) -> Dict:
        with gzip.open(self._gzip_path, 'rb') as file:
            return json.loads(file.read())

    def next_ssm_event(self) -> Iterable[SSMEvent]:
        for record in self.parse().get('Records', []):
            source = record.get('eventSource')

            if source == SSM_PRINCIPAL:
                yield SSMEvent(record)
