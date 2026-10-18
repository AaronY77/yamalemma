import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from yamalemma.credentials import load_key


class CredentialTests(unittest.TestCase):
    def test_private_file_and_environment_precedence(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict('os.environ', {}, clear=True):
            path = Path(directory) / 'key'
            path.write_text('synthetic-file-key\n')
            path.chmod(0o600)
            with patch('yamalemma.credentials.KEY_FILE', path):
                self.assertEqual(load_key(), 'synthetic-file-key')
                self.assertIsNone(load_key('CUSTOM_API_KEY'))
                with patch.dict('os.environ', {'OPENAI_API_KEY': 'synthetic-env-key'}):
                    self.assertEqual(load_key(), 'synthetic-env-key')

    def test_absent_key_is_explicit(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict('os.environ', {}, clear=True):
            with patch('yamalemma.credentials.KEY_FILE', Path(directory) / 'missing'):
                self.assertIsNone(load_key())

    def test_public_or_linked_file_rejected(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict('os.environ', {}, clear=True):
            path = Path(directory) / 'key'
            path.write_text('synthetic-file-key')
            path.chmod(0o644)
            with patch('yamalemma.credentials.KEY_FILE', path):
                with self.assertRaises(ValueError):
                    load_key()
            path.chmod(0o600)
            link = Path(directory) / 'link'
            link.symlink_to(path)
            with patch('yamalemma.credentials.KEY_FILE', link):
                with self.assertRaises(ValueError):
                    load_key()
