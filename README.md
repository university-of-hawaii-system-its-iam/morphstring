# Example Grouper-compatible password encryption for Python apps

A Python 3 command-line tool and library for Grouper-compatible morphString
password encryption. Verified against Grouper 6.4.1. Runtime requires Python
3.9 or newer and `cryptography`.

The purpose of this project is to borrow the Grouper strategy for reducing the
number of secrets to just one, the morphkey.

<!-- TOC -->
* [Example Grouper-compatible password encryption for Python apps](#example-grouper-compatible-password-encryption-for-python-apps)
    * [Install and run](#install-and-run)
    * [Shell wrapper](#shell-wrapper)
    * [Decryption example](#decryption-example)
    * [Regression tests](#regression-tests)
<!-- TOC -->

## Install and run

From this project's root:

```shell
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/morphstring -c
```

The command prompts for the encryption key and password without echo and
verifies the encrypted result. Use `-q` for ciphertext only. `-k KEY` and
`-v VALUE` accept explicit inputs; otherwise the corresponding environment
variable is `MORPHSTRING_ENCRYPT_KEY`, for example.

You can also run `python src/morph.py` after installing
`src/requirements-morph.txt`.

## Shell wrapper

To encrypt a password:

```shell
./src/morph.sh -c
./src/morph.sh -k je49jwna2jDNcb3 -v letmein7 -c -q
```

## Decryption example

This example provides code to use in a container project that will need to
decrypt passwords.

`src/decrypt_example.py` accepts a morph key and an encrypted password. Its
`decrypt_password(morphKey, morphValue)` function returns the decrypted
password as `rawValue`, using the project's Grouper-compatible key derivation.

```shell
.venv/bin/python src/decrypt_example.py
```

Missing inputs are prompted for without echo. You can also supply `-k`/`--key`
and `-v`/`--value`, or use `GROUPER_MORPHSTRING_ENCRYPT_KEY` and
`MORPH_ENCRYPTED_VALUE`. Explicit arguments take precedence. The program prints
the decrypted password to standard output.

Example with the public test key and dummy ciphertext:

```shell
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

```shell
.venv/bin/python -B -m unittest discover -s src/tests -p 'test_*.py' -v
```

The suite preserves 32 fixed vectors produced by the actual Grouper 6.4.1 jar.
An optional Java harness reproduces the original 63 comparison cases; see
[algorithm details and verification instructions](src/README-morph.md).
