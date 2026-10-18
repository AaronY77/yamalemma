import datetime
import json
from pathlib import Path

from yamalemma.domain import fingerprint, load_json, save_json


def freeze_protocol(dataset, configurations, destination):
    if len(configurations) < 2:
        raise ValueError('evaluation requires at least two declared configurations')
    if not dataset:
        raise ValueError('evaluation dataset is empty')
    ids, groups = set(), {}
    for row in dataset:
        if row['item_fingerprint'] in ids:
            raise ValueError('duplicate evaluation item')
        ids.add(row['item_fingerprint'])
        if row.get('label') not in ('defect', 'control', 'unlabeled'):
            raise ValueError('invalid evaluation label')
        if row.get('split') not in ('development', 'heldout') or not row.get('group'):
            raise ValueError('evaluation needs explicit provenance groups and splits')
        if row.get('label') != 'unlabeled' and not all(row.get(key) for key in ('reviewer', 'label_basis', 'provenance')):
            raise ValueError('labels require independent review and provenance; untouched items are not clean controls')
        if row['group'] in groups and groups[row['group']] != row['split']:
            raise ValueError('provenance group leaks across development and held-out splits')
        groups[row['group']] = row['split']
    protocol = {'schema_version': 1, 'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'dataset': dataset, 'configurations': {name: fingerprint(config) for name, config in configurations.items()},
                'scoring_version': 'item-level-reviewed-labels-v1',
                'denominators': 'missing runs count as missing; no claims do not certify faithfulness; unlabeled items excluded from accuracy',
                'contamination': 'public issues and historical development examples may occur in model training data'}
    protocol['fingerprint'] = fingerprint(protocol)
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('x') as stream:
        stream.write(json.dumps(protocol, ensure_ascii=False, indent=2) + '\n')
    return protocol


def verify_protocol(protocol):
    if fingerprint({key: value for key, value in protocol.items() if key != 'fingerprint'}) != protocol['fingerprint']:
        raise ValueError('evaluation protocol changed after freezing')


def ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def score(protocol, reports, configuration, config, judgments=None):
    verify_protocol(protocol)
    if protocol['configurations'].get(configuration) != fingerprint(config):
        raise ValueError('evaluation configuration differs from the frozen protocol')
    rows = {row['item_fingerprint']: row for row in protocol['dataset'] if row['split'] == 'heldout'}
    found = {}
    for report in reports:
        if report.get('hash') != fingerprint({key: value for key, value in report.items() if key != 'hash'}):
            raise ValueError('audit result hash mismatch')
        key = report.get('item_fingerprint')
        if key not in rows or key in found:
            raise ValueError('report is duplicate or outside the held-out protocol')
        if report.get('config_fingerprint') != fingerprint(config):
            raise ValueError('audit report used a different configuration')
        if report.get('protocol_fingerprint') != protocol['fingerprint']:
            raise ValueError('audit was not bound to this protocol before running')
        found[key] = report
    judgments = judgments or []
    available = {(report['hash'], fingerprint(row['claim'])): row for report in found.values() for row in report['claims']}
    reviewed = {}
    for judgment in judgments:
        identity = (judgment.get('audit_hash'), judgment.get('claim_fingerprint'))
        if identity not in available or identity in reviewed:
            raise ValueError('judgment is duplicate or does not match an exact audit claim')
        if not judgment.get('reviewer') or not judgment.get('justification'):
            raise ValueError('judgments require a reviewer and justification')
        if judgment.get('meaning') not in ('correct', 'incorrect', 'uncertain'):
            raise ValueError('invalid meaning judgment')
        if judgment.get('direction') not in ('correct', 'incorrect', 'unreviewed'):
            raise ValueError('invalid correction-direction judgment')
        if judgment['direction'] != 'unreviewed' and 'fix' not in available[identity]:
            raise ValueError('direction judgment requires a recorded correction candidate')
        reviewed[identity] = judgment
    known_defects = {key for key, row in rows.items() if row['label'] == 'defect'}
    reader_hits, confirmed, confirmed_correct = set(), set(), set()
    checked, unresolved, total_claims, internal_errors = 0, 0, 0, 0
    by_bridge, costs, unknown_costs, seconds = {}, 0.0, 0, 0.0
    reviewed_confirmed, correct_confirmed, reviewed_direction, correct_direction = 0, 0, 0, 0
    proof_attempts, claims_with_attempts, model_calls, reused_calls = 0, 0, 0, 0
    for key, report in found.items():
        if report['reader_claims'] and key in known_defects:
            reader_hits.add(key)
        costs += report.get('new_cost_usd', 0)
        unknown_costs += report.get('unknown_cost_calls', 0)
        seconds += report.get('elapsed_seconds', 0)
        model_calls += len(report.get('model_calls', []))
        reused_calls += sum(call.get('reused', False) for call in report.get('model_calls', []))
        for claim in report['claims']:
            total_claims += 1
            proof_attempts += len(claim.get('evidence', []))
            claims_with_attempts += bool(claim.get('evidence'))
            verdict = claim['adjudication']
            formal = verdict.get('evidence_verdict', 'UNRESOLVED')
            checked += formal == 'EVIDENCE-CHECKED'
            unresolved += formal == 'UNRESOLVED'
            internal_errors += formal == 'INTERNAL-ERROR'
            bridge = claim['claim']['bridges'][0]['type']
            counts = by_bridge.setdefault(bridge, {'claims': 0, 'checked': 0, 'confirmed': 0, 'reviewed_confirmed': 0, 'correct_confirmed': 0})
            counts['claims'] += 1
            counts['checked'] += formal == 'EVIDENCE-CHECKED'
            if verdict.get('finding_status') == 'confirmed' and rows[key]['label'] != 'unlabeled':
                confirmed.add(key)
                confirmed_correct.update({key} if key in known_defects else set())
                counts['confirmed'] += 1
            judgment = reviewed.get((report['hash'], fingerprint(claim['claim'])))
            if judgment:
                if verdict.get('finding_status') == 'confirmed' and judgment['meaning'] != 'uncertain':
                    reviewed_confirmed += 1
                    correct_confirmed += judgment['meaning'] == 'correct'
                    counts['reviewed_confirmed'] += 1
                    counts['correct_confirmed'] += judgment['meaning'] == 'correct'
                if judgment['direction'] != 'unreviewed':
                    reviewed_direction += 1
                    correct_direction += judgment['direction'] == 'correct'
    for counts in by_bridge.values():
        counts['reviewed_precision'] = ratio(counts['correct_confirmed'], counts['reviewed_confirmed'])
    return {'protocol_fingerprint': protocol['fingerprint'], 'configuration': configuration,
            'scope': 'item-level reviewed labels; does not independently validate claim meaning or direction',
            'heldout_items': len(rows), 'completed_reports': len(found), 'missing_reports': len(rows) - len(found),
            'labeled_defects': len(known_defects), 'reader_detected_defect_items': len(reader_hits),
            'reader_item_recall': ratio(len(reader_hits), len(known_defects)),
            'confirmed_item_precision': ratio(len(confirmed_correct), len(confirmed)),
            'confirmed_item_recall': ratio(len(confirmed_correct), len(known_defects)),
            'reader_recall_retained': ratio(len(confirmed_correct & reader_hits), len(reader_hits)),
            'formal_claims': total_claims, 'evidence_checked': checked, 'unresolved_rate': ratio(unresolved, total_claims),
            'internal_errors': internal_errors, 'by_bridge': by_bridge,
            'meaning_judgments': len(reviewed), 'reviewed_confirmed_claims': reviewed_confirmed,
            'reviewed_confirmed_claim_precision': ratio(correct_confirmed, reviewed_confirmed),
            'formal_attempt_coverage': ratio(claims_with_attempts, total_claims), 'proof_attempts': proof_attempts,
            'model_calls': model_calls, 'reused_model_calls': reused_calls,
            'no_claim_items': sum(report.get('no_claim_detected', False) for report in found.values()),
            'incomplete_reader_items': sum(report['status'] != 'reviewed' for report in found.values()),
            'new_known_api_cost_usd': costs, 'unknown_cost_calls': unknown_costs,
            'cost_per_confirmed_item': ratio(costs, len(confirmed)) if unknown_costs == 0 else None,
            'seconds': seconds, 'direction_reviewed': reviewed_direction,
            'direction_accuracy': ratio(correct_direction, reviewed_direction),
            'direction_note': 'measured only over supplied human direction judgments; elaboration is insufficient',
            'judgments_fingerprint': fingerprint(judgments)}


def evaluate(worker, items, protocol, config, name, output, offline=False):
    from yamalemma.pipeline import run_audit
    verify_protocol(protocol)
    if protocol['configurations'].get(name) != fingerprint(config):
        raise ValueError('configuration is not frozen in this protocol')
    expected = {row['item_fingerprint'] for row in protocol['dataset'] if row['split'] == 'heldout'}
    if {item['fingerprint'] for item in items} != expected or len(items) != len(expected):
        raise ValueError('evaluation items differ from the frozen held-out set')
    output = Path(output)
    save_json(output / 'protocol.json', protocol)
    summaries = run_audit(worker, items, config, output, offline=offline, protocol=protocol['fingerprint'])
    result = score(protocol, [load_json(row['report']) for row in summaries], name, config)
    save_json(output / 'scores.json', result)
    return result
