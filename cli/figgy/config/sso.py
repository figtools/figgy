from figgy.config.constants import HOME

# OKTA Constants
OKTA_SESSION_DURATION = 43200
SUPPORTED_OKTA_FACTOR_TYPES = ['GOOGLE', 'OKTA']

FIGGY_KEYRING_NAMESPACE = "figgy"
FIGGY_KEYRING_ASSERTION_NAME = "okta_assertion"
OKTA_SESSION_CACHE_PATH = f"{HOME}/.figgy/cache/okta/session"
GOOGLE_SESSION_CACHE_PATH = f"{HOME}/.figgy/cache/google/session"

SAML_ASSERTION_CACHE_KEY = 'assertion'
SAML_ASSERTION_MAX_AGE = 60 * 5 * 1000  # Assertions don't last long, 5 mins max reuse
