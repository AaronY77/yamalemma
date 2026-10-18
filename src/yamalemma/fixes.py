import json
from pathlib import Path

from yamalemma.domain import fingerprint
from yamalemma.harness import BLOCKED
from yamalemma.prompts import FIX_SCHEMA, messages


def propose_fix(worker, client, item, claim, binding):
    call = client.complete('fixer', 'fix', messages(
        'Propose a corrected closed Lean proposition for this suspected discrepancy. Preserve relevant assumptions. '
        'Do not provide a proof or top-level commands. Do not assume the formal statement is the side that is wrong. '
        'If the official problem or answer is unavailable, direction must be unknown. This is a draft requiring interpretation review.',
        {'original_statement': item['expected_type'], 'supporting_declarations': item['context']['declarations'],
         'informal': item.get('informal'), 'docstring': item.get('docstring'), 'claim': claim}), FIX_SCHEMA, binding)
    result = {'status': call['status'], 'model_call': call, 'review_status': 'pending', 'faithfulness_certified': False}
    if call['status'] != 'completed':
        return result
    candidate = call['data']
    result['candidate'] = candidate
    if BLOCKED.search(candidate['statement']):
        result['status'] = 'policy_rejected'
        return result
    allowed = json.loads((Path(__file__).parent / 'proof_syntax.json').read_text())
    context = item['context']
    response = worker.request({'action': 'render', 'expected': candidate['statement'], 'allowed_syntax': allowed,
                               'context': context['declarations'], 'namespace': context['namespace'], 'scopes': context.get('scopes', [])})
    result.update(status='elaborated' if response.get('status') == 'rendered' else 'unresolved', elaboration=response)
    result['fingerprint'] = fingerprint(result)
    return result


def issue_draft(report):
    claim, verdict = report['claim'], report['adjudication']
    return '\n'.join([
        f'# Draft: {claim["id"]}', '', claim['explanation'], '',
        f'Formal evidence: {verdict["evidence_verdict"]}', f'Finding confirmation: {verdict["finding_status"]}',
        f'Scope: {claim["scope"]}', '', '## Proposition checked', '', '```lean', claim['proposition'], '```', '',
        '## Interpretation obligations', '',
        *[f'- {bridge["obligation"]} (discharged: {bridge["discharged"]})' for bridge in verdict['bridges']], '',
        '## Reproduction', '', f'Source fingerprint: {report["item"]["fingerprint"]}',
        'The attached report.json contains the exact proof attempts, source, environment and axiom audit.', '',
        'This is a local draft. Correction direction and interpretation require review before submission.', '',
    ])
