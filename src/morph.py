#!/usr/bin/env python3
"""Encrypt a Grouper morphString password without Docker or Java.

Install: python3 -m pip install -r src/requirements-morph.txt
Usage:   python3 src/morph.py [-k KEY] [-v VALUE] [-c] [-q]

Keys default to GROUPER_MORPHSTRING_ENCRYPT_KEY, values to MORPH_RAW_VALUE;
missing inputs are prompted for without echo, with password confirmation.
Use prompts or environment variables to keep secrets out of command arguments.

Compatibility: Grouper 6.4.1 Morph.key(), Morph.encrypt(), and Crypto.init()
with UTF-8 (the container default). Inputs are literal strings; this program
does not interpret Java properties escapes, EL expressions, or file paths.
See README-morph.md for the algorithm, upstream sources, and test command.
"""

import argparse
import base64
import getpass
import os
import sys
import unicodedata

try:
    from cryptography.hazmat.primitives import padding
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
except ModuleNotFoundError as error:
    if error.name != "cryptography":
        raise
    sys.exit("error: install dependencies with python3 -m pip install -r "
             "src/requirements-morph.txt")


def java_trim(value: str) -> str:
    """Java String.trim() removes only characters U+0000 through U+0020."""
    return value.strip("".join(chr(code) for code in range(33)))


def derive_key(encrypt_key: str) -> bytes:
    """Apply Morph.key()'s suffix and Crypto.init()'s character padding."""
    secret = java_trim(encrypt_key)
    # Grouper's isBlank() uses Java Character.isWhitespace(), which also
    # rejects Unicode separators except the three non-breaking spaces.
    if not secret or all(
        char in "\t\n\v\f\r\x1c\x1d\x1e\x1f"
        or (unicodedata.category(char) in ("Zs", "Zl", "Zp")
            and char not in "\u00a0\u2007\u202f")
        for char in secret
    ):
        raise ValueError("encrypt key must not be blank")

    # Java counts UTF-16 code units, rather than Unicode code points or bytes.
    units = (secret + "w").encode("utf-16-le", errors="surrogatepass")
    target = 16 if len(units) <= 32 else 32
    units = (units + b"x\x00" * target)[: target * 2]
    # Java's UTF-8 encoder replaces a surrogate split by truncation with '?'.
    key = units.decode("utf-16-le", errors="surrogatepass").encode(
        "utf-8", errors="replace"
    )
    if len(key) not in (16, 24, 32):
        raise ValueError("normalized key is not a valid AES byte length; use an ASCII key")
    return key


def encrypt(raw_value: str, encrypt_key: str) -> str:
    """Return the same Base64 ciphertext as Grouper's Morph.encrypt()."""
    data = java_trim(raw_value).encode("utf-8", errors="replace")
    padder = padding.PKCS7(128).padder()
    padded = padder.update(data) + padder.finalize()
    cipher = Cipher(algorithms.AES(derive_key(encrypt_key)), modes.ECB()).encryptor()
    return base64.b64encode(cipher.update(padded) + cipher.finalize()).decode("ascii")


def decrypt(encrypted_value: str, encrypt_key: str) -> str:
    """Decrypt this program's output, for round-trip verification.

    Base64 validation is intentionally stricter than Grouper's permissive
    decoder; valid Morph.encrypt() output works with either implementation.
    """
    data = base64.b64decode(java_trim(encrypted_value), validate=True)
    cipher = Cipher(algorithms.AES(derive_key(encrypt_key)), modes.ECB()).decryptor()
    padded = cipher.update(data) + cipher.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    return (unpadder.update(padded) + unpadder.finalize()).decode("utf-8")


def prompt_secret(label: str) -> str:
    if not sys.stdin.isatty():
        raise ValueError(f"{label} not supplied and stdin is not a terminal")
    return getpass.getpass(f"{label}: ")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-k", "--key", default=os.environ.get("GROUPER_MORPHSTRING_ENCRYPT_KEY"),
                        help="encrypt.key; otherwise use the environment or a hidden prompt")
    parser.add_argument("-v", "--value", default=os.environ.get("MORPH_RAW_VALUE"),
                        help="raw value; otherwise use the environment or a hidden prompt")
    parser.add_argument("-c", "--check", action="store_true",
                        help="verify decryption against the Grouper-trimmed input")
    parser.add_argument("-q", "--quiet", action="store_true", help="print only the encrypted value")
    args = parser.parse_args()
    try:
        key = args.key if args.key is not None else prompt_secret("morphString encrypt.key")
        raw = args.value
        if raw is None:
            raw = prompt_secret("Raw value to encrypt")
            if raw != prompt_secret("Confirm raw value"):
                raise ValueError("values did not match")
        if not raw:
            raise ValueError("raw value must not be empty")
        if "\n" in raw or "\r" in raw:
            raise ValueError("raw value must not contain a newline")
        result = encrypt(raw, key)
        if args.check:
            if decrypt(result, key) != java_trim(raw):
                raise ValueError("verification failed: decrypted value does not match the input")
            if not args.quiet:
                print("Verified: decrypts back to the Grouper-trimmed value.", file=sys.stderr)
    except (ValueError, EOFError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nCancelled.", file=sys.stderr)
        return 130

    if not args.quiet:
        print("\nEncrypted (morph) value for the .env file:")
    print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())
