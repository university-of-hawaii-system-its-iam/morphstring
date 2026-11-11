# morphstring

A Python 3 command-line tool and library for Grouper-compatible morphString
password encryption. Verified against Grouper 6.4.1. Runtime requires Python
3.9 or newer and `cryptography`; Docker and Java are unnecessary.

## Install and run

From this project's root:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/morphstring -c
```

The command prompts for the encryption key and password without echo and
verifies the encrypted result. Use `-q` for ciphertext only. `-k KEY` and
`-v VALUE` accept explicit inputs; otherwise the corresponding environment
variables are `GROUPER_MORPHSTRING_ENCRYPT_KEY` and `MORPH_RAW_VALUE`.

You can also run `python src/morph.py` after installing
`src/requirements-morph.txt`.

## Decryption example

`src/decrypt_example.py` accepts a morph key and an encrypted password. Its
`decrypt_password(morphKey, morphValue)` function returns the decrypted
password as `rawValue`, using the project's Grouper-compatible key derivation.

```sh
.venv/bin/python src/decrypt_example.py
```

Missing inputs are prompted for without echo. You can also supply `-k`/`--key`
and `-v`/`--value`, or use `GROUPER_MORPHSTRING_ENCRYPT_KEY` and
`MORPH_ENCRYPTED_VALUE`. Explicit arguments take precedence. The program prints
the decrypted password to standard output.

Example with the public test key and dummy ciphertext:

```sh
.venv/bin/python src/decrypt_example.py -k je49jwna2jDNcb3 -v 'h6KVnpDwSs9EML2hzZ9SMg=='
# letmein7
```

From Python code with the project `src/` directory on the import path:

```python
from decrypt_example import decrypt_password

morphKey = "je49jwna2jDNcb3"
morphValue = "h6KVnpDwSs9EML2hzZ9SMg=="
rawValue = decrypt_password(morphKey, morphValue)
```

## Regression tests

```sh
.venv/bin/python -B -m unittest discover -s src/tests -p 'test_*.py' -v
```

The suite preserves 32 fixed vectors produced by the actual Grouper 6.4.1 jar.
An optional Java harness reproduces the original 63 comparison cases; see
[algorithm details and verification instructions](src/README-morph.md).

## Layout

```text
pyproject.toml                 Package metadata and morphstring command
src/morph.py                  Encryption library and CLI
src/decrypt_example.py        Decryption function and runnable example
src/requirements-morph.txt     Runtime dependency for direct script use
src/README-morph.md            Algorithm, compatibility, and examples
src/tests/test_morph.py        Python regression suite
src/tests/test_decrypt_example.py  Decryption example regression tests
src/tests/morph-vectors.json   Saved Java-generated regression vectors
src/tests/verify_grouper.py    Optional comparison against a real Grouper jar
src/tests/MorphReference.java  Java helper for that comparison
```

All extracted files and regression resources live under `src/`.
