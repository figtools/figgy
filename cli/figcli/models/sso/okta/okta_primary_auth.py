import time
from dataclasses import dataclass

from figcli.models.defaults.defaults import CLIDefaults
from figcli.models.sso.okta.okta_session import OktaSession
from figcli.utils.utils import *
import logging
import requests
from figcli.models.sso.okta.okta_auth import OktaAuth

log = logging.getLogger(__name__)


# Pulled from / tweaked -> https://github.com/jmhale/okta-awscli/blob/master/oktaawscli/aws_auth.py

class OktaPrimaryAuth(OktaAuth):
    def __init__(self, defaults: CLIDefaults, password: str, mfa: str):
        super().__init__(defaults)
        self._user = defaults.user
        self._password = password
        self.https_base_url = f"https://{defaults.provider_config.base_url}"
        self.totp_token = mfa
        self.factor = self.factor_type
        self._session: OktaSession = None

    def get_session(self):
        return OktaSession(session_id=self._get_session().session_id,
                           session_token=self._get_session().session_token)

    def to_json(self) -> str:

        return json.dumps({
            OKTA_SESSION_TOKEN_CACHE_KEY: self.get_session().session_token,
            OKTA_SESSION_ID_CACHE_KEY: self.get_session().session_id
        })

    def _get_session(self) -> OktaSession:
        """ Performs primary auth against Okta """
        if self._session:
            return self._session

        auth_data = {
            "username": self._user,
            "password": self._password
        }
        resp = requests.post(self.https_base_url + '/api/v1/authn', json=auth_data)
        resp_json = resp.json()
        if 'status' in resp_json:
            if resp_json['status'] == 'MFA_REQUIRED':
                factors_list = resp_json['_embedded']['factors']
                state_token = resp_json['stateToken']
                session_token = self.verify_mfa(factors_list, state_token)
            elif resp_json['status'] == 'SUCCESS':
                session_token = resp_json['sessionToken']
            elif resp_json['status'] == 'MFA_ENROLL':
                log.warning("MFA not enrolled. Cannot continue. Please enroll a MFA factor in the Okta Web "
                            "UI first!")
                raise InvalidSessionError("Unable to auth through Okta.")
        elif resp.status_code != 200:
            log.error(resp_json['errorSummary'])
            raise InvalidSessionError("Unable to auth through Okta.")
        else:
            print("Error creating OKTA session. Perhaps invalid MFA. Please retry.")
            log.error(resp_json)
            raise InvalidSessionError("Unable to auth through Okta.")

        session_id = self.get_session_id(session_token)
        # Cache session for subsequent requests.
        self._session = OktaSession(session_token=session_token, session_id=session_id)

        return self._session

    def verify_mfa(self, factors_list, state_token) -> str:
        """ Performs MFA auth against Okta """

        supported_factor_types = ["token:software:totp", "push"]

        supported_factors = []
        for factor in factors_list:
            if factor['factorType'] in supported_factor_types:
                supported_factors.append(factor)
            else:
                log.info("Unsupported factorType: %s" %
                         (factor['factorType'],))

        supported_factors = sorted(supported_factors,
                                   key=lambda factor: (
                                       factor['provider'],
                                       factor['factorType']))
        if len(supported_factors) == 1:
            session_token = self.verify_single_factor(
                supported_factors[0], state_token)
        elif len(supported_factors) > 0:
            if not self.factor:
                print("Registered MFA factors:")
            for index, factor in enumerate(supported_factors):
                factor_type = factor['factorType']
                factor_provider = factor['provider']

                if factor_provider == "GOOGLE":
                    factor_name = "Google Authenticator"
                elif factor_provider == "OKTA":
                    if factor_type == "push":
                        factor_name = "Okta Verify - Push"
                    else:
                        factor_name = "Okta Verify"
                else:
                    factor_name = "Unsupported factor type: %s" % factor_provider

                if self.factor:
                    if self.factor == factor_provider:
                        factor_choice = index
                        log.info("Using pre-selected factor choice \
                                         from ~/.okta-aws")
                        break
                else:
                    print("%d: %s" % (index + 1, factor_name))
            if not self.factor:
                factor_choice = int(input('Please select the MFA factor: ')) - 1
            log.info("Performing secondary authentication using: %s" %
                     supported_factors[factor_choice]['provider'])
            session_token = self.verify_single_factor(supported_factors[factor_choice],
                                                      state_token)
        else:
            print("MFA required, but no supported factors enrolled! Exiting.")
            exit(1)
        return session_token

    def verify_single_factor(self, factor, state_token):
        """ Verifies a single MFA factor """
        req_data = {
            "stateToken": state_token
        }

        log.debug(factor)
        if factor['factorType'] == 'token:software:totp':
            if self.totp_token:
                log.debug("Using TOTP token from command line arg")
                req_data['answer'] = self.totp_token
            else:
                req_data['answer'] = input('Enter MFA token: ')

        post_url = factor['_links']['verify']['href']
        resp = requests.post(post_url, json=req_data)
        resp_json = resp.json()
        if 'status' in resp_json:
            if resp_json['status'] == "SUCCESS":
                return resp_json['sessionToken']
            elif resp_json['status'] == "MFA_CHALLENGE" and factor['factorType'] != 'u2f':
                print("Waiting for push verification...")
                while True:
                    resp = requests.post(
                        resp_json['_links']['next']['href'], json=req_data)
                    resp_json = resp.json()
                    if resp_json['status'] == 'SUCCESS':
                        return resp_json['sessionToken']
                    elif resp_json['factorResult'] == 'TIMEOUT':
                        print("Verification timed out")
                        exit(1)
                    elif resp_json['factorResult'] == 'REJECTED':
                        print("Verification was rejected")
                        exit(1)
                    else:
                        time.sleep(0.5)
        return None

    def get_session_id(self, session_token):
        """ Gets a session cookie from a session token """
        data = {"sessionToken": session_token}
        resp = requests.post(
            self.https_base_url + '/api/v1/sessions', json=data).json()

        if 'id' not in resp:
            raise InvalidSessionError("Failed to get session from OKTA.")

        return resp['id']
