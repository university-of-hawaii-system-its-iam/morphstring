#!/usr/bin/env python3
"""
Decrypt a Grouper morphString password and print the decrypted value.

Usage: python3 src/decrypt_example.py [-k MORPH_KEY] [-v ENCRYPTED_VALUE]

Missing inputs use GROUPER_MORPHSTRING_ENCRYPT_KEY and MORPH_ENCRYPTED_VALUE,
or hidden prompts. Requires the project's cryptography dependency.
"""

import argparse
import base64
import os
import sys

from morph import derive_key, java_trim, prompt_secret
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def decrypt_password(morphKey: str, morphValue: str) -> str:
    """
    Return the decrypted password for a literal key and Base64 morph value.

    derive_key() applies Grouper's key trimming, 'w' suffix, and 'x' padding
    or truncation. The remaining steps reverse its AES/ECB encryption.
    Invalid keys, ciphertext, padding, or UTF-8 raise ValueError.
    """
    encryptedBytes = base64.b64decode(java_trim(morphValue), validate=True)
    decryptor = Cipher(algorithms.AES(derive_key(morphKey)), modes.ECB()).decryptor()
    paddedBytes = decryptor.update(encryptedBytes) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    rawBytes = unpadder.update(paddedBytes) + unpadder.finalize()
    rawValue = rawBytes.decode("utf-8")
    return rawValue


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-k", "--key", dest="morphKey",
                        default=os.environ.get("GROUPER_MORPHSTRING_ENCRYPT_KEY"),
                        help="morphString encryption key; otherwise use the environment or a hidden prompt")
    parser.add_argument("-v", "--value", dest="morphValue",
                        default=os.environ.get("MORPH_ENCRYPTED_VALUE"),
                        help="Base64 encrypted password; otherwise use the environment or a hidden prompt")
    args = parser.parse_args()
    try:
        morphKey = args.morphKey
        if morphKey is None:
            morphKey = prompt_secret("morphString encrypt.key")
        morphValue = args.morphValue
        if morphValue is None:
            morphValue = prompt_secret("Encrypted morphString value")
        rawValue = decrypt_password(morphKey, morphValue)
    except (ValueError, EOFError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        return 130

    print(rawValue)
    return 0


if __name__ == "__main__":
    sys.exit(main())
