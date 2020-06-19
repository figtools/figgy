# Pulled from / tweaked -> https://github.com/jmhale/okta-awscli/blob/master/oktaawscli/aws_auth.py

""" Handles auth to Okta and returns SAML assertion """
import base64
# pylint: disable=C0325,R0912,C1801
import sys
from collections import namedtuple

import requests
from bs4 import BeautifulSoup as bs

from figcli.models.sso.okta.okta_auth import OktaAuth
from figcli.utils.utils import *

log = logging.getLogger(__name__)


class Okta:
    """ Handles auth to Okta and returns SAML assertion """

    def __init__(self, okta_auth: OktaAuth):
        self.app_link = okta_auth.app_link
        self.auth = okta_auth
        self.https_base_url = f"https://{okta_auth.base_url}"

    def get_apps(self, session_id):
        """ Gets apps for the user """
        sid = "sid=%s" % session_id
        headers = {'Cookie': sid}
        resp = requests.get(
            self.https_base_url + '/api/v1/users/me/appLinks',
            headers=headers).json()
        aws_apps = []
        for app in resp:
            if app['appName'] == "amazon_aws":
                aws_apps.append(app)
        if not aws_apps:
            log.error("No AWS apps are available for your user. \
                Exiting.")
            sys.exit(1)

        aws_apps = sorted(aws_apps, key=lambda app: app['sortOrder'])
        app_choice = 0 if len(aws_apps) == 1 else None
        if app_choice is None:
            print("Available apps:")
            for index, app in enumerate(aws_apps):
                app_name = app['label']
                print("%d: %s" % (index + 1, app_name))

            app_choice = int(input('Please select AWS app: ')) - 1
        log.info("Selected app: %s" % aws_apps[app_choice]['label'])
        return aws_apps[app_choice]['label'], aws_apps[app_choice]['linkUrl']

    def get_saml_assertion(self, html):
        """ Returns the SAML assertion from HTML """
        soup = bs(html.text, "html.parser")
        assertion = ''

        for input_tag in soup.find_all('input'):
            if input_tag.get('name') == 'SAMLResponse':
                assertion = input_tag.get('value')

        if not assertion:
            log.error("SAML assertion not valid: " + assertion)

        return assertion

    def get_assertion(self):
        """ Main method to get SAML assertion from Okta """
        session = self.auth.get_session()

        if not self.app_link:
            print("dafuq??")
            # app_name, app_link = self.get_apps(session_id)
        else:
            app_name = None
            app_link = self.app_link
        sid = "sid=%s" % session.session_id
        headers = {'Cookie': sid}
        resp = requests.get(app_link, headers=headers)
        assertion = self.get_saml_assertion(resp)
        if len(assertion) < 20:
            raise InvalidSessionError("Invalid assertion returned from OKTA")

        return assertion

    @staticmethod
    def extract_available_roles_from(assertion):
        aws_attribute_role = 'https://aws.amazon.com/SAML/Attributes/Role'
        attribute_value_urn = '{urn:oasis:names:tc:SAML:2.0:assertion}AttributeValue'
        roles = []
        role_tuple = namedtuple("RoleTuple", ["principal_arn", "role_arn"])
        root = ET.fromstring(base64.b64decode(assertion))
        for saml2attribute in root.iter('{urn:oasis:names:tc:SAML:2.0:assertion}Attribute'):
            if saml2attribute.get('Name') == aws_attribute_role:
                for saml2attributevalue in saml2attribute.iter(attribute_value_urn):
                    roles.append(role_tuple(*saml2attributevalue.text.split(',')))
        return roles
