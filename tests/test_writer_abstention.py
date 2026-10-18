import json
import tempfile
import unittest
from pathlib import Path

from test_next_models import configuration, response
from yamalemma.domain import make_claim
from yamalemma.models import ModelClient
from yamalemma.pipeline import prove_claim


def item():
    return {'id': 'synthetic', 'fingerprint': 'synthetic-item', 'context': {'namespace': '', 'declarations': []}}


class WriterAbstentionTests(unittest.TestCase):
    def test_abstention_stops_the_polarity_without_a_proof_check(self):
        claim = make_claim(item(), 'c1', 'True', 'synthetic prediction', 'scope', 'synthetic scope', 'parse', 'synthetic obligation')
        replies = []

        def transport(url, body, headers, timeout):
            replies.append(json.loads(body['messages'][1]['content'])['expected'])
            return response({'proof': None, 'abstain_reason': 'cannot prove this in Lean'})

        with tempfile.TemporaryDirectory() as directory:
            client = ModelClient(configuration(), Path(directory) / 'models', transport=transport)
            attempts, calls, verdict = prove_claim(None, client, item(), claim, {'source': 'fixed'}, Path(directory) / 'claim', repairs=1)
        self.assertEqual(replies, ['True', 'Not (True)'])
        self.assertEqual(attempts, [])
        self.assertEqual(len(calls), 2)
        self.assertEqual(verdict['evidence_verdict'], 'UNRESOLVED')
        self.assertEqual([entry['polarity'] for entry in verdict['writer_abstentions']], ['confirm', 'refute'])
        self.assertEqual(verdict['writer_abstentions'][0]['reason'], 'cannot prove this in Lean')

    def test_empty_proof_counts_as_abstention(self):
        claim = make_claim(item(), 'c2', 'True', 'synthetic prediction', 'scope', 'synthetic scope', 'parse', 'synthetic obligation')
        with tempfile.TemporaryDirectory() as directory:
            client = ModelClient(configuration(), Path(directory) / 'models',
                                 transport=lambda *args: response({'proof': '  ', 'abstain_reason': None}))
            attempts, calls, verdict = prove_claim(None, client, item(), claim, {'source': 'fixed'}, Path(directory) / 'claim', repairs=1)
        self.assertEqual(attempts, [])
        self.assertEqual(verdict['writer_abstentions'][1]['reason'], 'no proof returned')


if __name__ == '__main__':
    unittest.main()
