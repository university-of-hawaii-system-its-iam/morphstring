"""Check the decryption example against saved Grouper-generated ciphertext."""

import json
import os
from pathlib import Path
import subprocess
import sys
import unittest

import decrypt_example


class DecryptExampleTest(unittest.TestCase):
    def test_saved_grouper_vectors(self):
        vectors = json.loads((Path(__file__).with_name("morph-vectors.json")).read_text())["vectors"]
        for index, vector in enumerate(vectors):
            with self.subTest(index=index):
                rawValue = decrypt_example.decrypt_password(vector["key"], vector["encrypted"])
                self.assertEqual(rawValue, vector["raw"].strip("".join(map(chr, range(33)))))

    def test_invalid_ciphertext(self):
        with self.assertRaises(ValueError):
            decrypt_example.decrypt_password("je49jwna2jDNcb3", "not base64!")

    def test_command_line_inputs(self):
        result = subprocess.run(
            [sys.executable, "-B", str(Path(decrypt_example.__file__).resolve()),
             "-k", "je49jwna2jDNcb3", "-v", "h6KVnpDwSs9EML2hzZ9SMg=="],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "letmein7\n")
        self.assertEqual(result.stderr, "")

    def test_environment_inputs(self):
        environment = dict(os.environ, GROUPER_MORPHSTRING_ENCRYPT_KEY="je49jwna2jDNcb3",
                           MORPH_ENCRYPTED_VALUE="h6KVnpDwSs9EML2hzZ9SMg==")
        result = subprocess.run(
            [sys.executable, "-B", str(Path(decrypt_example.__file__).resolve())],
            input="", capture_output=True, text=True, env=environment, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "letmein7\n")


if __name__ == "__main__":
    unittest.main()
