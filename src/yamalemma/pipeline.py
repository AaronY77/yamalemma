import time
from pathlib import Path

from yamalemma.adjudicate import adjudicate
from yamalemma.domain import fingerprint, file_hash, make_probe, save_json
from yamalemma.harness import BLOCKED, check_probe, environment_record, render_target, validate_item
from yamalemma.models import ModelClient
from yamalemma.precheck import precheck
from yamalemma.prompts import (PROMPT_VERSION, READER_SCHEMA, WRITER_SCHEMA, BACKTRANSLATION_SCHEMA, COMPARISON_SCHEMA,
                               backtranslation_messages, reader_messages, writer_messages, prepare_claim, messages)
from yamalemma.report import write_report
from yamalemma.storage import ArtifactStore
from yamalemma.worker import WorkerError


def first_error(evidence):
    error = evidence.get('attempt', {}).get('error') or evidence.get('reason', 'proof not accepted')
    return error.split('\n\n', 1)[0][:2000]


def prove_claim(worker, client, item, claim, binding, directory, repairs=3):
    attempts, model_calls, abstentions = [], [], []
    store = ArtifactStore(Path(directory) / 'artifacts')
    for polarity in ('confirm', 'refute'):
        previous, diagnostic = None, None
        for attempt in range(repairs + 1):
            expected = claim['proposition'] if polarity == 'confirm' else f'Not ({claim["proposition"]})'
            call = client.complete('writer', 'proof', writer_messages(item, claim, expected, previous, diagnostic),
                                   WRITER_SCHEMA, dict(binding, claim=fingerprint(claim), polarity=polarity, attempt=attempt))
            model_calls.append(call)
            if call['status'] != 'completed':
                break
            proof = call['data'].get('proof')
            if not proof or not proof.strip():
                abstentions.append({'polarity': polarity, 'attempt': attempt,
                                    'reason': (call['data'].get('abstain_reason') or 'no proof returned')[:2000]})
                break
            previous = proof
            probe = make_probe(claim, polarity, previous)
            try:
                evidence = check_probe(worker, item, claim, probe, store)
            except (WorkerError, OSError, TimeoutError) as error:
                verdict = adjudicate(claim, attempts)
                verdict['infrastructure_error'] = str(error)[:2000]
                verdict['writer_abstentions'] = abstentions
                write_report(Path(directory), item, claim, attempts, verdict)
                save_json(Path(directory) / 'model_calls.json', model_calls)
                return attempts, model_calls, verdict
            attempts.append(evidence)
            if evidence['accepted']:
                break
            diagnostic = first_error(evidence)
    verdict = adjudicate(claim, attempts)
    verdict['writer_abstentions'] = abstentions
    write_report(Path(directory), item, claim, attempts, verdict)
    save_json(Path(directory) / 'model_calls.json', model_calls)
    return attempts, model_calls, verdict


def audit_item(worker, client, item, config, directory, protocol=None):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    start_calls = len(client.calls)
    result = {'item_id': item['id'], 'item': item, 'item_fingerprint': item.get('fingerprint'), 'status': 'pending',
              'reader_claims': [], 'claims': [], 'rejected_candidates': [], 'advisory': None,
              'finding_status': 'unconfirmed', 'prompt_version': PROMPT_VERSION,
              'config_fingerprint': fingerprint(config), 'protocol_fingerprint': protocol}
    checks = precheck(worker, item)
    result['prechecks'] = checks
    if item.get('unsupported') or 'expected_type' not in item:
        result.update(status='unsupported_source', reasons=checks.get('reasons', []))
    else:
        validate_item(item, worker.project)
        binding = {'item': item['fingerprint'], 'environment': environment_record(worker.project)['fingerprint'],
                   'config': fingerprint(config), 'prompts': PROMPT_VERSION, 'protocol': protocol,
                   'implementation': {name: file_hash(Path(__file__).parent / name) for name in ('models.py', 'prompts.py', 'pipeline.py', 'config.py', 'fixes.py', 'budget.py', 'credentials.py')}}
        advisory = None
        if config['stages']['backtranslation']:
            paraphrase = client.complete('backtranslator', 'backtranslation', backtranslation_messages(item, checks), BACKTRANSLATION_SCHEMA, binding)
            advisory = {'paraphrase_status': paraphrase['status'], 'differences': []}
            if paraphrase['status'] == 'completed':
                advisory['paraphrase'] = paraphrase['data']['paraphrase']
                comparison = client.complete('comparator', 'comparison', messages(
                    'Compare this literal paraphrase with the supplied informal problem. List possible differences only. These are advisory, not findings.',
                    {'paraphrase': paraphrase['data']['paraphrase'], 'informal': item.get('informal'), 'docstring': item.get('docstring')}), COMPARISON_SCHEMA, binding)
                advisory['comparison_status'] = comparison['status']
                if comparison['status'] == 'completed':
                    advisory['differences'] = comparison['data']['differences']
            result['advisory'] = advisory
        readers = ['reader'] + (['second_reader'] if config['stages']['second_reader'] else [])
        candidates, states, seen = [], [], set()
        for role in readers:
            call = client.complete(role, 'reader', reader_messages(item, checks, advisory), READER_SCHEMA, binding)
            states.append(call['status'])
            if call['status'] == 'completed':
                for candidate in call['data']['claims']:
                    key = fingerprint(candidate)
                    if key not in seen:
                        candidates.append(candidate)
                        seen.add(key)
        result['reader_statuses'] = states
        result['reader_claims'] = candidates
        result['status'] = 'reviewed' if all(state == 'completed' for state in states) else 'reader_incomplete'
        result['no_claim_detected'] = not candidates and all(state == 'completed' for state in states)
        result['claims_omitted_by_limit'] = max(0, len(candidates) - config['limits']['max_claims'])
        for index, candidate in enumerate(candidates[:config['limits']['max_claims']], 1):
            try:
                claim = prepare_claim(item, candidate, index)
            except ValueError as error:
                result['rejected_candidates'].append({'candidate': candidate, 'reason': str(error)})
                continue
            rendering = render_target(worker, item, claim['proposition'])
            if rendering.get('status') != 'rendered':
                reason = str(rendering.get('error') or rendering.get('status'))[:1000]
                result['rejected_candidates'].append({'candidate': candidate, 'reason': f'target does not elaborate: {reason}'})
                continue
            claim_directory = directory / f'claim-{index:02d}'
            if config['stages']['triage']:
                evidence, calls, verdict = prove_claim(worker, client, item, claim, binding, claim_directory, config['limits']['max_repairs'])
            else:
                evidence, calls = [], []
                verdict = adjudicate(claim, [])
                write_report(claim_directory, item, claim, evidence, verdict)
            row = {'claim': claim, 'adjudication': verdict, 'evidence': evidence,
                   'model_statuses': [call['status'] for call in calls], 'report_directory': claim_directory.name}
            if config['stages']['fixes'] and verdict.get('evidence_verdict') == 'EVIDENCE-CHECKED':
                from yamalemma.fixes import propose_fix
                row['fix'] = propose_fix(worker, client, item, claim, binding)
            result['claims'].append(row)
    result['model_calls'] = client.calls[start_calls:]
    result['elapsed_seconds'] = time.monotonic() - started
    result['new_cost_usd'] = sum(call['new_cost_usd'] for call in result['model_calls'] if call.get('new_cost_usd') is not None)
    result['unknown_cost_calls'] = sum(call.get('new_cost_usd') is None and call.get('reserved_usd', 0) > 0 for call in result['model_calls'])
    result['hash'] = fingerprint(result)
    save_json(directory / 'audit.json', result)
    lines = [f'# Audit: {item["id"]}', '', f'Status: {result["status"]}',
             f'Reader suspicions: {len(result["reader_claims"])}', f'Checked claims: {len(result["claims"])}', '',
             'No claim detected is not a certificate of faithfulness. Interpretation review remains separate.', '']
    for index, row in enumerate(result['claims'], 1):
        lines.append(f'- [Claim {index}]({row["report_directory"]}/report.md): {row["adjudication"].get("evidence_verdict", "infrastructure_error")}')
    (directory / 'audit.md').write_text('\n'.join(lines) + '\n')
    return result


def run_audit(worker, items, config, output, offline=False, client=None, protocol=None):
    import fcntl
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    with (output / '.run.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ValueError('another audit is already using this output directory') from error
        return run_locked_audit(worker, items, config, output, offline, client, protocol)


def run_locked_audit(worker, items, config, output, offline=False, client=None, protocol=None):
    output = Path(output)
    client = client or ModelClient(config, output / 'models', offline=offline)
    rows = []
    for index, item in enumerate(items):
        directory = output / 'items' / f'{index:04d}-{fingerprint(item)[:12]}'
        row = audit_item(worker, client, item, config, directory, protocol=protocol)
        rows.append({'item_id': item['id'], 'item_fingerprint': item.get('fingerprint'), 'status': row['status'],
                     'report': str(directory / 'audit.json'), 'hash': row['hash']})
        save_json(output / 'summary.json', rows)
        print(f'{item["id"]}: {row["status"]}', flush=True)
    return rows


def review_audit(worker, report, reviews):
    if report.get('hash') != fingerprint({key: value for key, value in report.items() if key != 'hash'}):
        raise ValueError('audit report changed after recording')
    if not isinstance(reviews, list):
        raise ValueError('reviews must be a list of explicit claim-bound sign-offs')
    import copy
    result = copy.deepcopy(report)
    for row in result['claims']:
        evidence = [check_probe(worker, result['item'], row['claim'], entry['probe']) for entry in row['evidence']]
        row['evidence'] = evidence
        row['adjudication'] = adjudicate(row['claim'], evidence, reviews)
    result['interpretation_reviews'] = reviews
    result['finding_status'] = 'confirmed' if any(row['adjudication']['finding_status'] == 'confirmed' for row in result['claims']) else 'unconfirmed'
    result['hash'] = fingerprint({key: value for key, value in result.items() if key != 'hash'})
    return result
