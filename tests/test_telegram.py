import os
import subprocess
import unittest
from unittest.mock import patch

from semanario.telegram import read_token, TokenError


class CredentialTest(unittest.TestCase):
    def test_encrypted_credential_is_read_without_pass(self):
        with patch.dict(os.environ, {"EDUSEMANARI_ENCRYPTED_TOKEN_FILE": "/unused/test.cred"}):
            with patch("semanario.telegram.subprocess.run", return_value=subprocess.CompletedProcess([], 0, "test-value\n")) as run:
                self.assertEqual(read_token("unused"), "test-value")
                self.assertEqual(run.call_count, 1)
                self.assertEqual(run.call_args.args[0][0], "systemd-creds")
                self.assertTrue(run.call_args.kwargs["capture_output"])

    def test_invalid_credential_fails_without_using_pass(self):
        with patch.dict(os.environ, {"EDUSEMANARI_ENCRYPTED_TOKEN_FILE": "/unused/test.cred"}):
            with patch("semanario.telegram.subprocess.run", side_effect=subprocess.CalledProcessError(1, "systemd-creds")) as run:
                with self.assertRaises(TokenError):
                    read_token("unused")
                self.assertEqual(run.call_count, 1)

    def test_empty_credential_is_rejected(self):
        with patch.dict(os.environ, {"EDUSEMANARI_ENCRYPTED_TOKEN_FILE": "/unused/test.cred"}):
            with patch("semanario.telegram.subprocess.run", return_value=subprocess.CompletedProcess([], 0, "")):
                with self.assertRaises(TokenError):
                    read_token("unused")
