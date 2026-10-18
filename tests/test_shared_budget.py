import multiprocessing
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from yamalemma.budget import BudgetError, budget_status, change_budget_limits, initialize_budget, reserve_hosted
from yamalemma.models import ModelClient
from yamalemma.prompts import PROOF_SCHEMA
from test_next_models import configuration, response


def reserve_in_process(path, index):
    with patch('yamalemma.budget.BUDGET_PATH', Path(path)):
        return reserve_hosted(0.01, str(index)) is not None


class SharedBudgetTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.path = self.root / 'shared.sqlite3'
        setting = patch('yamalemma.budget.BUDGET_PATH', self.path)
        setting.start()
        self.addCleanup(setting.stop)
        credentials = patch('yamalemma.models.load_key', return_value='synthetic-key')
        credentials.start()
        self.addCleanup(credentials.stop)

    def client(self, folder, transport=None, offline=False):
        return ModelClient(configuration('openai'), self.root / folder, offline=offline,
                           transport=transport or (lambda *args: response({'proof': 'by trivial'}, 'openai')))

    def call(self, client, index=0):
        return client.complete('writer', 'proof', [{'role': 'user', 'content': 'prove True'}], PROOF_SCHEMA, {'index': index})

    def test_new_run_folders_cannot_restart_shared_allowance(self):
        initialize_budget(2, 1)
        self.assertEqual(self.call(self.client('one'))['status'], 'completed')
        self.assertEqual(self.call(self.client('two'))['status'], 'completed')
        result = self.call(self.client('three', lambda *args: self.fail('over-budget network call')))
        self.assertEqual(result['status'], 'shared_budget_exhausted')
        self.assertEqual(budget_status()['calls'], 2)

    def test_paid_failures_retain_reservations_after_restart(self):
        initialize_budget(1, 1)
        def timeout(*args):
            raise TimeoutError()
        self.assertEqual(self.call(self.client('one', timeout))['status'], 'transport_error')
        self.assertGreater(budget_status()['reserved_usd'], 0)
        self.assertEqual(self.call(self.client('one'), 1)['status'], 'shared_budget_exhausted')

    def test_cache_and_offline_miss_do_not_consume_allowance(self):
        initialize_budget(1, 1)
        self.call(self.client('one'))
        before = budget_status()
        client = self.client('one', lambda *args: self.fail('replay network call'))
        self.assertTrue(self.call(client)['reused'])
        self.assertEqual(self.call(self.client('one', offline=True), 1)['status'], 'replay_miss')
        self.assertEqual(budget_status(), before)

    def test_cost_limit_blocks_before_network_even_with_calls_left(self):
        initialize_budget(3, 0.000001)
        result = self.call(self.client('one', lambda *args: self.fail('network call')))
        self.assertEqual(result['status'], 'shared_budget_exhausted')
        self.assertEqual(budget_status()['calls'], 0)

    def test_missing_and_corrupt_ledgers_fail_closed(self):
        self.assertEqual(self.call(self.client('one'))['status'], 'shared_budget_unavailable')
        self.assertFalse(self.path.exists())
        self.path.write_text('not a database')
        self.assertEqual(self.call(self.client('two'))['status'], 'shared_budget_unavailable')
        with self.assertRaises(BudgetError):
            budget_status()

    def test_import_preserves_usage_and_reinitialization_cannot_reset(self):
        result = initialize_budget(3, 0.25, 2, 0.109124)
        self.assertEqual(result['calls'], 2)
        self.assertEqual(result['reserved_usd'], 0.109124)
        with self.assertRaises(BudgetError):
            initialize_budget(100, 100)
        self.assertEqual(budget_status(), result)
        self.assertEqual(self.path.stat().st_mode & 0o777, 0o600)

    def test_concurrent_processes_cannot_overspend(self):
        initialize_budget(3, 1)
        with multiprocessing.get_context('spawn').Pool(4) as pool:
            accepted = pool.starmap(reserve_in_process, [(str(self.path), index) for index in range(12)])
        self.assertEqual(sum(accepted), 3)
        self.assertEqual(budget_status()['calls'], 3)
        self.assertEqual(budget_status()['reserved_usd'], 0.03)

    def test_crash_after_reservation_remains_counted(self):
        initialize_budget(1, 1)
        with patch('yamalemma.models.save_json', side_effect=OSError('simulated disk failure')):
            with self.assertRaises(OSError):
                self.call(self.client('one', lambda *args: self.fail('network call')))
        self.assertEqual(budget_status()['calls'], 1)
        self.assertEqual(self.call(self.client('two'))['status'], 'shared_budget_exhausted')

    def test_local_model_does_not_require_hosted_budget(self):
        client = ModelClient(configuration(), self.root / 'local', transport=lambda *args: response({'proof': 'by trivial'}))
        self.assertEqual(self.call(client)['status'], 'completed')
        self.assertFalse(self.path.exists())

    def test_invalid_initial_values_do_not_create_ledger(self):
        for arguments in [(True, 1), (0, 1), (1, float('nan')), (1, -1), (1, 1, 2, 0), (1, 1, 0, 2)]:
            with self.assertRaises(ValueError):
                initialize_budget(*arguments)
            self.assertFalse(self.path.exists())

    def test_explicit_limit_change_preserves_usage(self):
        initialize_budget(3, 0.25, 2, 0.109124)
        result = change_budget_limits(4, 0.5)
        self.assertEqual(result['calls'], 2)
        self.assertEqual(result['reserved_usd'], 0.109124)
        self.assertEqual(result['remaining_calls'], 2)
        for limits in [(1, 0.5), (4, 0.01)]:
            with self.assertRaises(ValueError):
                change_budget_limits(*limits)
        self.assertEqual(budget_status(), result)

    def test_money_rounding_never_increases_allowance(self):
        initialize_budget(3, 0.0000019)
        self.assertIsNone(reserve_hosted(0.0000011, 'too-large'))
        self.assertEqual(budget_status()['reserved_usd'], 0)
