import json
import tempfile
import unittest
from pathlib import Path

from test_next_models import configuration
from yamalemma.domain import fingerprint, load_json, save_json
from yamalemma.evaluation import freeze_protocol
from yamalemma.intake import collect_labels, export_packets, write_dataset


def item(name, commit='0123abc', origin=None):
    record = {'schema_version': 1, 'id': name, 'origin': origin or f'src/{name}.lean', 'benchmark_commit': commit,
              'snapshot_kind': 'supplied-source', 'source_sha256': 'synthetic', 'raw_source': f'theorem {name} : True := trivial',
              'span': {'start_byte': 0, 'end_byte': 10}, 'declaration_source': f'theorem {name} : True := trivial',
              'informal': 'Synthetic fixture statement.', 'docstring': '', 'binders': '', 'conclusion': 'True',
              'expected_type': 'True', 'proof': '@(trivial)', 'unsupported': []}
    record['fingerprint'] = fingerprint(record)
    return record


def answer(template, label='defect'):
    return dict(template, label=label, reviewer='synthetic fixture reviewer', label_basis='synthetic test label',
                source_reference='synthetic fixture source', independent_of_outputs=True)


class IntakeTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)

    def export(self, items, split='heldout', name='batch'):
        return export_packets(items, self.root / name, split, 'synthetic-batch')

    def test_packets_are_label_free_and_export_does_not_overwrite(self):
        manifest = self.export([item('a'), item('b')])
        self.assertEqual(len(manifest['packets']), 2)
        packet = load_json(self.root / 'batch' / manifest['packets'][0]['path'])
        self.assertNotIn('label', json.dumps(packet['item']))
        self.assertTrue(all(row['label'] is None for row in load_json(self.root / 'batch' / 'responses-template.json')))
        with self.assertRaises(FileExistsError):
            self.export([item('a')])

    def test_unsupported_unpinned_changed_and_pipeline_items(self):
        unsupported = {'id': 'u', 'status': 'unsupported', 'reason': 'synthetic unsupported source'}
        manifest = self.export([item('a'), item('b', commit=None), unsupported])
        self.assertEqual([entry['id'] for entry in manifest['packets']], ['a'])
        self.assertEqual({entry['id'] for entry in manifest['excluded']}, {'b', 'u'})
        development = self.export([item('b', commit=None)], split='development', name='development')
        self.assertEqual(len(development['packets']), 1)
        changed = item('c')
        changed['informal'] = 'edited after ingestion'
        with self.assertRaisesRegex(ValueError, 'changed after ingestion'):
            self.export([changed], name='changed')
        report = item('d')
        report['claims'] = []
        report['fingerprint'] = fingerprint({key: value for key, value in report.items() if key != 'fingerprint'})
        with self.assertRaisesRegex(ValueError, 'pipeline outputs'):
            self.export([report], name='report')

    def test_unanswered_items_stay_unlabeled_and_labels_need_review(self):
        manifest = self.export([item('a'), item('b')])
        templates = load_json(self.root / 'batch' / 'responses-template.json')
        rows, summary = collect_labels(manifest, self.root / 'batch', [answer(templates[0])])
        self.assertEqual([row['label'] for row in rows], ['defect', 'unlabeled'])
        self.assertEqual(summary['unanswered'], 1)
        self.assertNotIn('reviewer', rows[1])
        for key, value in (('reviewer', ''), ('source_reference', ' '), ('independent_of_outputs', None)):
            with self.assertRaises(ValueError):
                collect_labels(manifest, self.root / 'batch', [dict(answer(templates[0]), **{key: value})])
        with self.assertRaises(ValueError):
            collect_labels(manifest, self.root / 'batch', [answer(templates[0], label='clean')])

    def test_responses_bind_to_exact_packets(self):
        manifest = self.export([item('a'), item('b')])
        templates = load_json(self.root / 'batch' / 'responses-template.json')
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            collect_labels(manifest, self.root / 'batch', [answer(templates[0]), answer(templates[0])])
        with self.assertRaisesRegex(ValueError, 'packet in this batch'):
            collect_labels(manifest, self.root / 'batch', [dict(answer(templates[0]), packet_fingerprint='other')])
        with self.assertRaisesRegex(ValueError, 'does not match its packet'):
            collect_labels(manifest, self.root / 'batch', [dict(answer(templates[0]), item_fingerprint=templates[1]['item_fingerprint'])])
        with self.assertRaisesRegex(ValueError, 'split is fixed'):
            collect_labels(manifest, self.root / 'batch', [dict(answer(templates[0]), split='development')])
        path = self.root / 'batch' / manifest['packets'][0]['path']
        packet = load_json(path)
        packet['item']['informal'] = 'edited packet'
        save_json(path, packet)
        with self.assertRaisesRegex(ValueError, 'changed after export'):
            collect_labels(manifest, self.root / 'batch', [])

    def test_collected_dataset_freezes_and_keeps_groups_together(self):
        manifest = export_packets([item('a', origin='src/p1.lean'), item('b', origin='src/p1.lean'), item('c')],
                                  self.root / 'batch', 'heldout', 'synthetic-batch')
        templates = load_json(self.root / 'batch' / 'responses-template.json')
        self.assertEqual(templates[0]['group'], templates[1]['group'])
        rows, summary = collect_labels(manifest, self.root / 'batch', [answer(templates[0]), answer(templates[2], 'control')])
        write_dataset(rows, self.root / 'dataset.json')
        with self.assertRaises(FileExistsError):
            write_dataset(rows, self.root / 'dataset.json')
        config = configuration()
        protocol = freeze_protocol(rows, {'one': config, 'two': config}, self.root / 'protocol.json')
        self.assertEqual(len(protocol['dataset']), 3)
        self.assertEqual(summary['labels'], {'defect': 1, 'control': 1, 'unlabeled': 1})
        leaked = [dict(row) for row in rows] + [dict(rows[0], item_fingerprint='other', split='development')]
        with self.assertRaisesRegex(ValueError, 'leaks'):
            freeze_protocol(leaked, {'one': config, 'two': config}, self.root / 'leaked.json')


if __name__ == '__main__':
    unittest.main()
