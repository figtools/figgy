import base64

from figcli.utils.utils import *


class KmsSvc:
    """
    Provides access to KMS apis
    """

    def __init__(self, boto_kms_client):
        self._kms = boto_kms_client

    def is_encrypted(self, obj: str):
        try:
            self.decrypt(obj)
            return True
        except Exception as e:
            return False

    def decrypt(self, base64_ciphertext):
        ciphertext = base64.b64decode(base64_ciphertext)
        return self._kms.decrypt(CiphertextBlob=ciphertext)[u"Plaintext"].decode()

    def decrypt_with_context(self, base64_ciphertext, context: Dict):
        ciphertext = base64.b64decode(base64_ciphertext)
        return self._kms.decrypt(
            CiphertextBlob=ciphertext,
            EncryptionContext=context)[u"Plaintext"].decode()
