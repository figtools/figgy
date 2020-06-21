from figcli.utils.utils import *
import platform
import keyring
import pyotp
from figcli.config import *
from keyring.backends.OS_X import Keyring
from keyring.backends.Windows import WinVaultKeyring
from keyrings.alt.file import EncryptedKeyring, PlaintextKeyring
import os


class SecretsManager:

    @staticmethod
    def set_keyring():
        if platform.system() == WINDOWS:
            keyring.set_keyring(WinVaultKeyring())
        elif os.environ.get(OVERRIDE_KEYRING_ENV_VAR) == "true":  # Used in builds when running tests
            keyring.set_keyring(PlaintextKeyring())
        elif platform.system() == MAC:
            keyring.set_keyring(keyring.backends.OS_X.Keyring())
        elif platform.system() == LINUX:
            keyring.set_keyring(EncryptedKeyring())
        else:
            Utils.stc_error_exit("Only OSX and MAC and Linux with installed SecretStorage are supported for "
                                 "OKTA + Keyring integration.")

    @staticmethod
    def generate_mfa(user: str) -> str:
        SecretsManager.set_keyring()
        mfa_secret = keyring.get_password(FIGGY_KEYRING_NAMESPACE, f'{user}-mfa')
        token = pyotp.TOTP(mfa_secret).now()
        print(f"Authenticating with one-time token: {token}")
        return token

    @staticmethod
    def set_mfa_secret(user: str, mfa_secret: str):
        SecretsManager.set_keyring()
        keyring.set_password(FIGGY_KEYRING_NAMESPACE, f'{user}-mfa', mfa_secret)

    @staticmethod
    def set_password(user: str, password: str) -> None:
        SecretsManager.set_keyring()
        keyring.set_password(FIGGY_KEYRING_NAMESPACE, user, password)

    @staticmethod
    def get_or_set(user: str, backup: str):
        current = SecretsManager.get_password(user)
        if not current:
            SecretsManager.set_password(user, backup)

        return current

    @staticmethod
    def get_password(user: str) -> str:
        if platform.system() == WINDOWS:
            keyring.set_keyring(WinVaultKeyring())
        elif os.environ.get(OVERRIDE_KEYRING_ENV_VAR) == "true":  # Used in circleci builds for running tests
            keyring.set_keyring(PlaintextKeyring())
        elif platform.system() == MAC:
            keyring.set_keyring(keyring.backends.OS_X.Keyring())
        elif platform.system() == LINUX:
            keyring.set_keyring(EncryptedKeyring())
        else:
            Utils.stc_error_exit("Only OSX and MAC are supported for OKTA + Keyring integration.")

        return keyring.get_password(FIGGY_KEYRING_NAMESPACE, user)
