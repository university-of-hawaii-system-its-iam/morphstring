"""Regression tests for the local morph.sh/morph.py wrapper."""

import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest

SRC = Path(__file__).resolve().parent.parent
KEY = "je49jwna2jDNcb3"  # Public test key only.
ENCRYPTED = "h6KVnpDwSs9EML2hzZ9SMg==\n"


class MorphShellTest(unittest.TestCase):
    def run_shell(self, *args, script=None, cwd=None, automatic=False, **overrides):
        environment = os.environ.copy()
        for name in ("MORPH_PYTHON", "GROUPER_MORPHSTRING_ENCRYPT_KEY", "MORPH_RAW_VALUE"):
            environment.pop(name, None)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        if not automatic:
            environment["MORPH_PYTHON"] = sys.executable
        environment.update(overrides)
        return subprocess.run([str(script or SRC / "morph.sh"), *args],
                              cwd=cwd, env=environment, input="", text=True, capture_output=True)

    def assert_quiet(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, ENCRYPTED)
        self.assertEqual(result.stderr, "")

    def test_arguments_and_verification(self):
        self.assert_quiet(self.run_shell("-k", KEY, "-v", "letmein7", "-c", "-q"))

    def test_environment_inputs(self):
        self.assert_quiet(self.run_shell("-c", "-q",
            GROUPER_MORPHSTRING_ENCRYPT_KEY=KEY, MORPH_RAW_VALUE="letmein7"))

    def test_grouper_trimming(self):
        self.assert_quiet(self.run_shell("-k", KEY, "-v", "  letmein7\t", "-c", "-q"))

    def test_nonquiet_result(self):
        result = self.run_shell("-k", KEY, "-v", "letmein7", "-c")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(ENCRYPTED, result.stdout)
        self.assertIn("Verified:", result.stderr)

    def test_input_errors(self):
        cases = [(("-q",), "stdin is not a terminal"),
                 (("-k", KEY, "-v", "first\nsecond"), "must not contain a newline"),
                 (("-g", "6.4.1"), "unrecognized arguments: -g")]
        for args, message in cases:
            with self.subTest(args=args):
                result = self.run_shell(*args)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)
                self.assertEqual(result.stdout, "")

    def test_help_without_interpreter(self):
        result = self.run_shell("-h", MORPH_PYTHON="/missing/python")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("MORPH_PYTHON", result.stdout)

    def test_missing_interpreter(self):
        result = self.run_shell("-q", MORPH_PYTHON="/missing/python")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Python interpreter not found", result.stderr)

    def test_missing_dependency(self):
        with tempfile.TemporaryDirectory() as directory:
            interpreter = Path(directory) / "python without cryptography"
            interpreter.write_text("#!/bin/sh\nexit 1\n")
            interpreter.chmod(0o755)
            result = self.run_shell("-q", MORPH_PYTHON=str(interpreter))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cryptography is required", result.stderr)

    def test_missing_local_implementation(self):
        with tempfile.TemporaryDirectory() as directory:
            script = Path(directory) / "morph.sh"
            shutil.copy2(SRC / "morph.sh", script)
            result = self.run_shell("-q", script=script)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("morph.py not found alongside", result.stderr)

    def test_relocated_project_with_spaces_and_local_venv(self):
        with tempfile.TemporaryDirectory(prefix="morph project ") as directory:
            project = Path(directory) / "project with spaces"
            source = project / "src"
            source.mkdir(parents=True)
            for name in ("morph.sh", "morph.py"):
                shutil.copy2(SRC / name, source / name)
            interpreter = project / ".venv/bin/python3"
            interpreter.parent.mkdir(parents=True)
            interpreter.write_text("#!/bin/sh\nexec " + shlex.quote(sys.executable) + ' "$@"\n')
            interpreter.chmod(0o755)
            result = self.run_shell("-k", KEY, "-v", "letmein7", "-c", "-q",
                script=source / "morph.sh", cwd=directory, automatic=True)
            self.assert_quiet(result)


if __name__ == "__main__":
    unittest.main()
