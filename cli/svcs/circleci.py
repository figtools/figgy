import logging
from dataclasses import dataclass
from typing import Dict

import requests

log = logging.getLogger(__name__)


@dataclass
class CircleResponse:
    status_code: int
    data: Dict


class CircleCi:

    def __init__(self, token: str):
        self._token = token

    def submit_job(self, repository: str, tag: str = None, revision: str = None,
                   extra_params: Dict = None) -> CircleResponse:
        """
        Submit a new job to CircleCi
        :param repository: circleci repo to trigger build for
        :param tag: tag to trigger a build on. Cannot be supplied if revision is set
        :param revision: githash to trigger a build for. Cannot be supplied if tag is set
        :param extra_params: Dict - Map of environment variables to add to the CircleCi build
        :return: CircleCi response. Response code and data in the CircleCi API response.
        """
        if tag and revision:
            raise ValueError("You cannot provide both a `tag` and a `revision`, you must select one or the other.")

        request_url = f"https://circleci.com/api/v1.1/project/github/Snagajob/{repository}?circle-token={self._token}"
        headers, content = {'Content-Type': 'application/json'}, {}

        if tag:
            content['tag'] = tag
        elif revision:
            content['revision'] = revision

        if extra_params:
            content['build_parameters'] = extra_params

        result = requests.post(request_url, json=content, headers=headers)
        return CircleResponse(data=result.json(), status_code=result.status_code)
