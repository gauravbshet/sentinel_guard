import os
from typing import Tuple

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def generate_key() -> bytes:
    return AESGCM.generate_key(bit_length=256)


def get_env_key() -> bytes:
    key_b64 = os.getenv("AES_KEY_B64")
    if not key_b64:
        # In production, require AES_KEY_B64. For dev, generate ephemeral.
        return generate_key()
    import base64

    return base64.b64decode(key_b64)


def encrypt_bytes(plaintext: bytes, key: bytes | None = None) -> Tuple[bytes, bytes]:
    if key is None:
        key = get_env_key()
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext, None)
    return nonce, ciphertext


def decrypt_bytes(nonce: bytes, ciphertext: bytes, key: bytes | None = None) -> bytes:
    if key is None:
        key = get_env_key()
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, None)
