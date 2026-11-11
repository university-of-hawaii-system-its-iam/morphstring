#!/bin/bash
#
# morphkey.sh - create a 4096-character random alphanumeric MorphString encryption key.
#
# Entropy for 48 characters: 285.8 bits, extremely string, beyond practical brute-force attack.
# LC_ALL=C prevents macOS tr from interpreting /dev/urandom as UTF-8.
#

echo "Pick one of the following as the new morphkey:"
for _ in {1..5}; do
    LC_ALL=C tr -dc 'a-zA-Z0-9' < /dev/urandom | fold -w 48 | head -n 1
done
echo