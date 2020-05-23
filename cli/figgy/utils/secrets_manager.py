from utils.utils import *
import platform
import keyring
from config import *
from keyring.backends.OS_X import Keyring
from keyring.backends.Windows import WinVaultKeyring
from keyrings.alt.file import EncryptedKeyring, PlaintextKeyring
import os


class SecretsManager:

    @staticmethod
    def set_password(user: str, password: str) -> None:
        if platform.system() == WINDOWS:
            keyring.set_keyring(WinVaultKeyring())
        elif platform.system() == MAC:
            keyring.set_keyring(keyring.backends.OS_X.Keyring())
        elif os.environ.get(OVERRIDE_KEYRING_ENV_VAR) == "true":  # Used in circleci builds for running tests
            keyring.set_keyring(PlaintextKeyring())
        elif platform.system() == LINUX:
            keyring.set_keyring(EncryptedKeyring())
        else:
            Utils.stc_error_exit("Only OSX and MAC and Linux with installed SecretStorage are supported for "
                                 "OKTA + Keyring integration.")

        keyring.set_password(FIGGY_KEYRING_NAMESPACE, user, password)

    @staticmethod
    def get_password(user: str) -> str:
        if platform.system() == WINDOWS:
            keyring.set_keyring(WinVaultKeyring())
        elif platform.system() == MAC:
            keyring.set_keyring(keyring.backends.OS_X.Keyring())
        elif os.environ.get(OVERRIDE_KEYRING_ENV_VAR) == "true":  # Used in circleci builds for running tests
            keyring.set_keyring(PlaintextKeyring())
        elif platform.system() == LINUX:
            keyring.set_keyring(EncryptedKeyring())
        else:
            Utils.stc_error_exit("Only OSX and MAC are supported for OKTA + Keyring integration.")

        return keyring.get_password(FIGGY_KEYRING_NAMESPACE, user)
