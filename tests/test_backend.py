import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from yamalemma.domain import fingerprint, make_claim, make_probe
from yamalemma.harness import check_probe
from yamalemma.ingest import ingest_source
from yamalemma.worker import LeanWorker


ROOT = Path(__file__).resolve().parents[1]


class BackendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.worker = LeanWorker(ROOT / 'lean')
        cls.worker.start()

    @classmethod
    def tearDownClass(cls):
        cls.worker.close()

    def item_and_claim(self, source=None):
        source = source or 'import Mathlib\ntheorem sample : (0 : Nat) = 0 := by rfl\n'
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'sample.lean'
            path.write_bytes(source.encode())
            item = ingest_source(self.worker, path)[-1]
        claim = make_claim(item, 'sample', item['expected_type'], 'sample prediction', 'coercion_junk',
                           'selected expression', 'parse', 'check relevance')
        return item, claim

    def test_supporting_names_and_helpers_are_preserved(self):
        source = ('import Mathlib\nnamespace Sample\n'
                  'def target (n : Nat) : Nat := n\n'
                  'theorem helper (n : Nat) : target n = n := by unfold target; rfl\n'
                  'theorem sample (n : Nat) : target n = n := by exact helper n\nend Sample\n')
        item, claim = self.item_and_claim(source)
        evidence = check_probe(self.worker, item, claim, make_probe(claim, 'confirm', item['proof']))
        self.assertTrue(evidence['accepted'], evidence)
        self.assertEqual([entry['name'] for entry in item['context']['declarations']], ['Sample.target', 'Sample.helper'])
        response = self.worker.request({'expected': 'True', 'proof': 'by have := Sample.helper; trivial'})
        self.assertEqual(response['status'], 'failure')

    def test_source_bytes_and_unicode_span_are_preserved(self):
        source = 'import Mathlib\r\n-- αβγ\r\ntheorem sample (n : ℕ) : n = n := by rfl\r\n'
        item, claim = self.item_and_claim(source)
        span = item['span']
        self.assertEqual(item['raw_source'], source)
        self.assertEqual(item['declaration_source'], source.encode()[span['start_byte']:span['end_byte']].decode())
        evidence = check_probe(self.worker, item, claim, make_probe(claim, 'confirm', item['proof']))
        self.assertTrue(evidence['accepted'], evidence)

    def test_anonymous_example_does_not_taint_later_theorem(self):
        item, claim = self.item_and_claim('import Mathlib\nexample : True := by sorry\ntheorem sample : True := by trivial\n')
        evidence = check_probe(self.worker, item, claim, make_probe(claim, 'confirm', item['proof']))
        self.assertTrue(evidence['accepted'], evidence)

    def test_admitted_support_cannot_validate_a_finding(self):
        source = 'import Mathlib\ntheorem helper : False := by sorry\ntheorem sample : False := helper\n'
        item, claim = self.item_and_claim(source)
        evidence = check_probe(self.worker, item, claim, make_probe(claim, 'confirm', item['proof']))
        self.assertFalse(evidence['accepted'])
        response = self.worker.request({'expected': item['expected_type'], 'proof': item['proof'],
                                        'context': item['context']['declarations']})
        self.assertEqual(response['status'], 'checked')
        self.assertIn('sorryAx', response['axioms'])

    def test_expected_type_dependencies_are_audited(self):
        response = self.worker.request({'expected': 'p = p', 'proof': 'by rfl',
                                        'context': [{'name': 'p', 'type': 'Prop', 'value': 'sorry'}]})
        self.assertEqual(response['status'], 'checked')
        self.assertIn('sorryAx', response['axioms'])

    def test_universe_polymorphic_statement(self):
        item, claim = self.item_and_claim('import Mathlib\ntheorem sample (α : Type*) (a : α) : a = a := by rfl\n')
        evidence = check_probe(self.worker, item, claim, make_probe(claim, 'confirm', item['proof']))
        self.assertTrue(evidence['accepted'], evidence)

    def test_unsupported_context_is_explicit(self):
        item, claim = self.item_and_claim('import Mathlib\nvariable (n : Nat)\ntheorem sample : n = n := by rfl\n')
        evidence = check_probe(self.worker, item, claim, make_probe(claim, 'confirm', item['proof']))
        self.assertFalse(evidence['accepted'])
        self.assertEqual(evidence['attempt']['status'], 'unsupported')

    def test_actual_kernel_check(self):
        result = self.worker.request({'expected': '(0 : Nat) = 0', 'proof': 'by rfl'})
        self.assertEqual(result['status'], 'checked')
        self.assertTrue(result['type_matches'])
        self.assertEqual(result['axioms'], [])

    def test_new_numeric_literals_use_existing_syntax(self):
        item, claim = self.item_and_claim('import Mathlib\ntheorem sample : (123456789 : Nat) = 123456789 := by rfl\n')
        evidence = check_probe(self.worker, item, claim, make_probe(claim, 'confirm', item['proof']))
        self.assertTrue(evidence['accepted'], evidence)

    def test_sorry_is_not_accepted(self):
        item, claim = self.item_and_claim()
        evidence = check_probe(self.worker, item, claim, make_probe(claim, 'confirm', 'by sorry'))
        self.assertFalse(evidence['accepted'])
        self.assertIn('sorryAx', evidence['forbidden_axioms'])

    def test_wrong_statement_cannot_pass(self):
        result = self.worker.request({'expected': '(0 : Nat) = 1', 'proof': 'by rfl'})
        self.assertEqual(result['status'], 'failure')

    def test_changed_probe_target_is_rejected(self):
        item, claim = self.item_and_claim()
        probe = make_probe(claim, 'confirm', 'by rfl')
        probe['expected'] = 'True'
        with self.assertRaises(ValueError):
            check_probe(self.worker, item, claim, probe)

    def test_source_tampering_is_rejected(self):
        item, claim = self.item_and_claim()
        item['raw_source'] += 'changed'
        with self.assertRaises(ValueError):
            check_probe(self.worker, item, claim, make_probe(claim, 'confirm', 'by rfl'))

    def test_changed_source_environment_is_rejected(self):
        item, claim = self.item_and_claim()
        item['environment']['manifest_sha256'] = 'changed'
        item['fingerprint'] = fingerprint({key: value for key, value in item.items() if key != 'fingerprint'})
        claim['item_fingerprint'] = item['fingerprint']
        with self.assertRaisesRegex(ValueError, 'environment differs'):
            check_probe(self.worker, item, claim, make_probe(claim, 'confirm', 'by rfl'))

    def test_command_escape_is_rejected(self):
        result = self.worker.request({'expected': 'True', 'proof': 'by trivial\naxiom evil : False'})
        self.assertEqual(result['status'], 'failure')

    def test_executable_proof_syntax_is_rejected(self):
        item, claim = self.item_and_claim()
        evidence = check_probe(self.worker, item, claim, make_probe(claim, 'confirm', 'by run_tac IO.println "forged"'))
        self.assertFalse(evidence['accepted'])
        self.assertEqual(evidence['attempt']['status'], 'policy_rejected')

    def test_candidate_state_is_not_reused(self):
        first = self.worker.request({'expected': 'True', 'proof': 'by trivial'})
        second = self.worker.request({'expected': 'True', 'proof': 'YamalemmaChecked'})
        self.assertEqual(first['status'], 'checked')
        self.assertEqual(second['status'], 'failure')

    def test_sandbox_hides_home_and_credentials(self):
        command = self.worker.command
        prefix = command[:command.index('--') + 1]
        code = ('import json,os,pathlib,socket; '
                's=socket.socket(); s.settimeout(1); '
                'print(json.dumps({"secret":os.getenv("YAMALEMMA_TEST_SECRET"), '
                f'"source_visible":pathlib.Path({str(ROOT / "src")!r}).exists(), '
                '"routes":pathlib.Path("/proc/net/route").read_text().count("\\n")}))')
        env = dict(os.environ, YAMALEMMA_TEST_SECRET='test sentinel')
        response = json.loads(subprocess.check_output(prefix + ['/usr/bin/python3', '-c', code], env=env, text=True))
        self.assertIsNone(response['secret'])
        self.assertFalse(response['source_visible'])
        self.assertEqual(response['routes'], 1)

    def test_z_timeout_restarts_worker(self):
        generation = self.worker.generation
        result = self.worker.request({'expected': 'True', 'proof': 'by repeat skip'}, timeout=0.001)
        self.assertEqual(result['status'], 'timeout')
        self.assertIsNone(self.worker.process)
        result = self.worker.request({'expected': 'True', 'proof': 'by trivial'})
        self.assertEqual(result['status'], 'checked')
        self.assertEqual(self.worker.generation, generation + 1)
