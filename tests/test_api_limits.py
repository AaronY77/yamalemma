import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

from yamalemma.config import load_config
from yamalemma.models import ModelClient
from yamalemma.prompts import PROOF_SCHEMA


ROOT = Path(__file__).resolve().parents[1]


class ApiLimitTests(unittest.TestCase):
    def setUp(self):
        from yamalemma.budget import initialize_budget
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        setting = patch('yamalemma.budget.BUDGET_PATH', Path(directory.name) / 'budget.sqlite3')
        setting.start()
        self.addCleanup(setting.stop)
        initialize_budget(100, 100)

    def test_test_profile_counts_failures_and_preserves_cap_after_restart(self):
        config = load_config(ROOT / 'configs/hosted-smoke.toml')
        self.assertEqual(config['limits']['max_calls'], 3)
        self.assertEqual(config['limits']['max_cost_usd'], 0.25)
        self.assertEqual(config['limits']['max_repairs'], 0)
        self.assertEqual(config['limits']['max_claims'], 1)
        requests = []

        def transport(*args):
            requests.append(True)
            raise urllib.error.HTTPError('https://api.openai.com/v1/responses', 429, 'test rate limit', {}, None)

        with tempfile.TemporaryDirectory() as directory, patch.dict('os.environ', {'OPENAI_API_KEY': 'synthetic-test-key'}):
            for index in range(4):
                client = ModelClient(config, directory, transport=transport)
                result = client.complete('writer', 'cap-test', [{'role': 'user', 'content': 'prove True'}], PROOF_SCHEMA, {'attempt': index})
                self.assertEqual(result['status'], 'rate_limited' if index < 3 else 'budget_exhausted')
            self.assertEqual(len(requests), 3)
            self.assertLessEqual(client.spent, 0.25)

    def test_cost_reservation_blocks_before_network(self):
        config = load_config(ROOT / 'configs/hosted-smoke.toml')
        with tempfile.TemporaryDirectory() as directory, patch.dict('os.environ', {'OPENAI_API_KEY': 'synthetic-test-key'}):
            client = ModelClient(config, directory, transport=lambda *args: self.fail('request exceeded cost budget'))
            client.spent = 0.24
            result = client.complete('writer', 'cap-test', [{'role': 'user', 'content': 'prove True'}], PROOF_SCHEMA, {})
            self.assertEqual(result['status'], 'budget_exhausted')
            self.assertEqual(client.call_count, 0)
