import re
import json
from pathlib import Path

from yamalemma.axiom_policy import assess_axioms
from yamalemma.ingest import wrap
from yamalemma.harness import BLOCKED, validate_item


PATTERNS = {
    'unconstrained_limit': r'\b(?:limUnder|leftLim)\b',
    'summability_review': r'\btsum\b|∑\x27',
    'natural_arithmetic_review': r'ℕ|\bNat\b',
    'finite_index_review': r'\bFin\b',
    'division_review': r'/',
    'totalized_operation_review': r'\b(?:sSup|sInf|deriv)\b',
}


def precheck(worker, item):
    signature = item.get('signature_source', '')
    hints = [{'kind': name, 'status': 'advisory'} for name, pattern in PATTERNS.items() if re.search(pattern, signature)]
    result = {'item_id': item['id'], 'item_fingerprint': item.get('fingerprint'), 'hints': hints}
    if item.get('unsupported') or 'expected_type' not in item:
        return dict(result, status='unresolved', reasons=item.get('unsupported', [item.get('reason', 'unsupported source')]))
    validate_item(item, worker.project)
    allowed = json.loads((Path(__file__).parent / 'proof_syntax.json').read_text())
    context = item['context']
    support = {'context': context['declarations'], 'namespace': context['namespace'],
               'scopes': context.get('scopes', []), 'allowed_syntax': allowed}
    terms = [item['expected_type']] + [entry[key] for entry in context['declarations'] for key in ('type', 'value')]
    if any(BLOCKED.search(term) for term in terms):
        return dict(result, status='unresolved', reasons=['unsupported executable syntax in source type'])
    result['rendering'] = worker.request({'action': 'render', 'expected': item['expected_type'], **support})
    binders = item['binders']
    expected = f'∀ {binders}, False' if binders else 'False'
    expected = wrap(expected, context['opens'])
    attempt = worker.request({'expected': expected, 'proof': 'by intros; first | simp_all | omega | decide',
                              'heartbeats': 30000, **support}, timeout=10)
    result['vacuity_attempt'] = attempt
    result['vacuity'] = 'unresolved'
    if attempt.get('status') == 'checked' and attempt.get('type_matches') is True:
        axioms = attempt.get('axioms')
        if isinstance(axioms, list) and assess_axioms(tuple(axioms)).status == 'allowed':
            result['vacuity'] = 'contradictory_hypotheses_checked'
    result['status'] = 'completed' if result['rendering'].get('status') == 'rendered' else 'unresolved'
    if result['status'] == 'unresolved':
        result['reasons'] = [result['rendering'].get('error', 'target could not be rendered')]
    result['scope'] = 'advisory prechecks; no faithfulness verdict'
    return result
