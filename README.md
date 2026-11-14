# Example Grouper-compatible password encryption for Python apps

The purpose of this project is to replicate the Grouper strategy for reducing
the number of secrets to just one, the morphkey.

Runtime requires Python 3.9 or newer and `cryptography`.

## Overview

Without morphkey, the Unified API project has the following secrets to manage:
```
JWT_SECRET_KEY: ${JWT_SECRET_KEY}
IAM_PASSWORD: ${IAM_PASSWORD}
IWT_PASSWORD: ${IWT_PASSWORD}
EL_SYS_TOKEN: ${EL_SYS_TOKEN}
MP_PASSWORD: ${MP_PASSWORD}
MP_CIPHER_PASS: ${MP_CIPHER_PASS}
UHIMS_PASSWORD: ${UHIMS_PASSWORD}
UHIMS_WS_PASSWORD: ${UHIMS_WS_PASSWORD}
RMQ_PASSWORD: ${RMQ_PASSWORD}
AUTH_PASSWORD: ${AUTH_PASSWORD}
```
After implementing the morphkey strategy, only one secret is needed:
```
MORPH_KEY: ${MORPH_KEY}
```
The application will use the morphkey to decrypt the secrets (morphvalues) at 
runtime. The encrypted values can be stored in a `.env`, for example:
```
JWT_SECRET_KEY: VffnvluaRk2wql3ve74TMxpn4zOEKf905QksXv0YKmUwca5w
```
Use the shell scripts to create both the morphkey and the encrypted values.

## Python Decryption Function

This project provides code for a Python function to use in a container project 
that will need to decrypt passwords.

Copy from `src/decrypt_example.py` the function `decrypt_password()` into your project.

## Shell wrappers

Generate a set of morphkeys, one of which can be used to encrypt passwords
for your containerized app. Be sure to store it in BitWardin for safe keeping.

```shell
./src/morphkey.sh
```

Encrypt a password. These are the encrypted values to use in your `.env` file.
You will be prompted for the morphkey and the password (2x) to encrypt. No 
secrets are exposed on the command line.

```shell
./src/morph.sh
```
