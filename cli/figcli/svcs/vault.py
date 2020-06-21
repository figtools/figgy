from figcli.utils.secrets_manager import SecretsManager
from figcli.utils.utils import Utils
from cryptography.fernet import Fernet

"""
Largely taken from simple-crypt, but removing pycrypto requirement, instead using pycryptodome.
Slight tuning to account for faster encrypt/decrypt speeds. Remember, Figgy _only_ deals with temporary
access keys. Nothing in the vault should be valid longer than 12 hours from the time it was originally added
to the vault.
"""


class DecryptionException(Exception): pass


class EncryptionException(Exception): pass


class FiggyVault:

    def __init__(self):
        encryption_key = SecretsManager.get_password('figgy-encryption-key')
        if not encryption_key:
            Utils.wipe_vaults()
            encryption_key: str = Fernet.generate_key().decode()
            SecretsManager.set_password('figgy-encryption-key', encryption_key)

        self.fernet = Fernet(encryption_key)

    def encrypt(self, data):
        """
        Encrypt some data.  Input can be bytes or a string (which will be encoded
        using UTF-8).

        @param data: The data to be encrypted.

        @return: The encrypted data, as bytes.
        """
        return self.fernet.encrypt(self._str_to_bytes(data))

    def decrypt(self, data):
        """
        Decrypt some data.  Input must be bytes.

        @param data: The data to be decrypted, typically as bytes.

        @return: The decrypted data, as bytes.  If the original message was a
        string you can re-create that using `result.decode('utf8')`.
        """
        return self.fernet.decrypt(data)

    @staticmethod
    def _str_to_bytes(data):
        u_type = type(b''.decode('utf8'))
        if isinstance(data, u_type):
            return data.encode('utf8')
        return data
