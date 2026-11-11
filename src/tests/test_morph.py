"""Regression vectors produced by the actual Grouper 6.4.1 client jar."""

import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

import morph


HERE = Path(__file__).resolve().parent
TEST_KEY = "je49jwna2jDNcb3"  # Repository's public test key only.


class MorphTest(unittest.TestCase):
    def test_grouper_java_vectors(self):
        fixtures = json.loads((HERE / "morph-vectors.json").read_text())
        for index, vector in enumerate(fixtures["vectors"]):
            with self.subTest(index=index):
                self.assertEqual(morph.encrypt(vector["raw"], vector["key"]),
                                 vector["encrypted"])
                self.assertEqual(morph.decrypt(vector["encrypted"], vector["key"]),
                                 morph.java_trim(vector["raw"]))

    def test_characters_after_32_key_units_are_discarded(self):
        self.assertEqual(morph.encrypt("password", "a" * 32 + "first"),
                         morph.encrypt("password", "a" * 32 + "second"))

    def test_invalid_keys(self):
        for key in ("", " \t ", "\u2003" * 4, "é" * 16):
            with self.subTest(key=key), self.assertRaises(ValueError):
                morph.encrypt("password", key)

    def test_decrypt_rejects_invalid_ciphertext(self):
        for value in ("not base64!", "AAAA", ""):
            with self.subTest(value=value), self.assertRaises(ValueError):
                morph.decrypt(value, TEST_KEY)

    def run_cli(self, *args, **environment):
        env = os.environ.copy()
        env.pop("GROUPER_MORPHSTRING_ENCRYPT_KEY", None)
        env.pop("MORPH_RAW_VALUE", None)
        env.update(environment)
        return subprocess.run([sys.executable, "-B", str(Path(morph.__file__).resolve()), *args],
                              input="", text=True, capture_output=True, env=env)

    def test_quiet_cli_and_environment(self):
        result = self.run_cli("-c", "-q", GROUPER_MORPHSTRING_ENCRYPT_KEY=TEST_KEY,
                              MORPH_RAW_VALUE="letmein7")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "h6KVnpDwSs9EML2hzZ9SMg==\n")
        self.assertEqual(result.stderr, "")

    def test_cli_arguments_override_environment(self):
        result = self.run_cli("-k", TEST_KEY, "-v", "letmein7", "-q",
                              GROUPER_MORPHSTRING_ENCRYPT_KEY="different",
                              MORPH_RAW_VALUE="different")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "h6KVnpDwSs9EML2hzZ9SMg==\n")

    def test_check_uses_grouper_trimmed_value(self):
        result = self.run_cli("-k", TEST_KEY, "-v", "  letmein7\t", "-c", "-q")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "h6KVnpDwSs9EML2hzZ9SMg==\n")

    def test_noninteractive_missing_input_fails_without_echo(self):
        result = self.run_cli("-q")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("stdin is not a terminal", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_cli_rejects_empty_or_multiline_values(self):
        for raw in ("", "first\nsecond", "first\rsecond"):
            with self.subTest(raw=raw):
                result = self.run_cli("-k", TEST_KEY, "-v", raw, "-q")
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, "")


if __name__ == "__main__":
    unittest.main()
