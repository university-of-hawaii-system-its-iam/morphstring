#!/usr/bin/env bash
#
# morph.sh - encrypt (and optionally verify) a Grouper morphString value.
#
# Runs morph.py alongside this script using Python 3 and cryptography.
# From the morphstring project root, install dependencies with:
#   python3 -m venv .venv
#   .venv/bin/python -m pip install -e .
#
# Usage:
#   ./src/morph.sh [-k <encrypt-key>] [-v <raw-value>] [-c] [-q]
#
#   -k  morphString encrypt.key. Defaults to $GROUPER_MORPHSTRING_ENCRYPT_KEY,
#       otherwise prompted for (hidden input).
#   -v  Raw value to encrypt. Defaults to $MORPH_RAW_VALUE, otherwise prompted
#       for (hidden input, with confirmation).
#   -c  Verify by decrypting and comparing to the Grouper-trimmed raw value.
#   -q  Quiet: print only the encrypted value (useful for scripting).
#   -h  Show this help.
#
# Configuration:
#   MORPH_PYTHON     Python interpreter; defaults to morphstring/.venv/bin/python3
#                    when available, otherwise python3 from PATH.
#
# Examples:
#   ./src/morph.sh -c
#   ./src/morph.sh -k je49jwna2jDNcb3 -v letmein7 -q
#   MORPH_RAW_VALUE="$PASS" ./src/morph.sh -k "$KEY" -q
#
# Output is deterministic. Grouper trims leading/trailing password whitespace.
# The former -g option is removed; this script no longer selects a Grouper image.

set -euo pipefail

die() {
  printf 'error: %s\n' "$*" >&2
  exit 1
}

case "${1:-}" in
  -h|--help)
    sed -n '2,/^$/ { s/^# \{0,1\}//; p; }' "$0"
    exit 0
    ;;
esac

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd -- "$SCRIPT_DIR/.." && pwd)"
MORPH_SCRIPT="$SCRIPT_DIR/morph.py"

[ -r "$MORPH_SCRIPT" ] ||
  die "morph.py not found alongside this script: $MORPH_SCRIPT"

if [ -n "${MORPH_PYTHON:-}" ]; then
  PYTHON_BIN="$MORPH_PYTHON"
elif [ -x "$PROJECT_DIR/.venv/bin/python3" ]; then
  PYTHON_BIN="$PROJECT_DIR/.venv/bin/python3"
else
  PYTHON_BIN=python3
fi

command -v "$PYTHON_BIN" >/dev/null 2>&1 ||
  die "Python interpreter not found: $PYTHON_BIN; set MORPH_PYTHON to a Python 3 interpreter"

"$PYTHON_BIN" -c 'import cryptography' >/dev/null 2>&1 ||
  die "cryptography is required; install with: \"$PYTHON_BIN\" -m pip install -r \"$SCRIPT_DIR/requirements-morph.txt\""

exec "$PYTHON_BIN" "$MORPH_SCRIPT" "$@"
