from config.constants import HOME

# OKTA Constants
OKTA_SESSION_DURATION = 43200
SUPPORTED_OKTA_FACTOR_TYPES = ['GOOGLE', 'OKTA']

FIGGY_KEYRING_NAMESPACE = "figgy"
FIGGY_KEYRING_ASSERTION_NAME = "okta_assertion"
OKTA_SESSION_CACHE_PATH = f"{HOME}/.figgy/devops/cache/okta/session"
GOOGLE_SESSION_CACHE_PATH = f"{HOME}/.figgy/devops/cache/google/session"


