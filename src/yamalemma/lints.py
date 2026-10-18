import time
from pathlib import Path

from yamalemma.adjudicate import adjudicate
from yamalemma.domain import file_hash, fingerprint, save_json
from yamalemma.harness import environment_record, render_target, validate_item
from yamalemma.prompts import PROMPT_VERSION, edit_kind, prepare_claim
from yamalemma.report import write_report
from yamalemma.signature import binder_groups, declaration_signature, identifiers, text, walk


BINDER_SUFFIXES = ('term∀__,_»', 'term∃__,_»', 'term∃_,_»', 'Term.forall', 'Term.fun', 'term∃!_,_»')
IMPLICATIONS = ('Lean.Parser.Term.arrow', '«term_↔_»')
CONNECTIVES = ('«term_∧_»', '«term_∨_»')


def is_binder(node):
    return node['kind'].endswith(BINDER_SUFFIXES)


def binder_names(node):
    if node['kind'].endswith('binderIdent'):
        return {leaf['identifier'] for leaf in walk(node) if leaf['kind'] == 'ident' and leaf.get('identifier')}
    if node['kind'] == 'null' or node['kind'].endswith(('Binder', 'Binders')):
        names = set()
        for child in node.get('children', []):
            names |= binder_names(child)
        return names
    return set()


def declared_names(binder):
    names = set()
    for child in binder.get('children', [])[:-1]:
        names |= binder_names(child)
    names.discard('[anonymous]')
    return names


def body(binder):
    return binder['children'][-1]


def inner(paren):
    return paren['children'][1]


def shadowing(binder):
    names = declared_names(binder)
    found = []
    for part in walk(body(binder)):
        if part is not binder and is_binder(part):
            repeated = names & declared_names(part)
            if repeated:
                found.append({'names': sorted(repeated), 'inner': text(part)})
    return found


def captured_conjunction(binder):
    top = body(binder)
    if top['kind'] not in IMPLICATIONS or len(top['children']) < 3:
        return None
    left, operator, right = top['children'][0], top['children'][1], top['children'][-1]
    if left['kind'] not in CONNECTIVES or len(left['children']) < 3:
        return None
    first, second = left['children'][0], left['children'][-1]
    if not (first['kind'] == 'Lean.Parser.Term.paren' and second['kind'] == 'Lean.Parser.Term.paren'):
        return None
    whole = text(binder)
    if not whole.endswith(text(top)):
        return None
    header = whole[:len(whole) - len(text(top))].rstrip()
    connective = text(left['children'][1])
    arrow = text(operator)
    regrouped = f'({header} {text(inner(first))}) {connective} ({text(second)} {arrow} {text(right)})'
    return {'source': whole, 'regrouped': regrouped, 'edit_kind': edit_kind(whole, regrouped)}


def lint_conclusion(conclusion_node, conclusion_text):
    findings = []
    for part in walk(conclusion_node):
        if not is_binder(part):
            continue
        shadows = shadowing(part)
        captured = captured_conjunction(part)
        if not shadows and not captured:
            continue
        finding = {'binder': text(part), 'shadowed_binders': shadows, 'captured_conjunction': captured}
        if captured and conclusion_text.count(captured['source']) == 1:
            finding['suggested_edit'] = {'edit_from': captured['source'], 'edit_to': captured['regrouped'],
                                         'kind': captured['edit_kind']}
        finding['strength'] = 'strong' if shadows and captured else 'weak'
        findings.append(finding)
    return findings


def witness_binders(binders, conclusion):
    groups = binder_groups(binders)
    others = [text(node) for node in binders.get('children', []) if not node['kind'].endswith(('explicitBinder', 'implicitBinder', 'strictImplicitBinder', 'instBinder'))]
    needed = identifiers(conclusion)
    kept = set()
    changed = True
    while changed:
        changed = False
        for index, group in enumerate(groups):
            if index not in kept and not group['instance'] and needed & set(group['names']):
                kept.add(index)
                needed |= set(group['uses'])
                changed = True
    parts = []
    for index, group in enumerate(groups):
        if index in kept:
            names = ' '.join(group['names'])
            parts.append(f'({names} : {group["type"]})' if group['type'] else f'({names})')
    return {'binders': ' '.join(parts), 'names': [name for index in sorted(kept) for name in groups[index]['names']],
            'dropped': [group['text'] for index, group in enumerate(groups) if index not in kept] + others}


def lint_item(worker, item):
    record = {'item_id': item.get('id'), 'item_fingerprint': item.get('fingerprint'), 'findings': [],
              'scope': 'deterministic parse lint; a finding is a suspicion about grouping, not a confirmed defect'}
    found = declaration_signature(worker, item)
    if found['status'] != 'found':
        return dict(record, **found)
    record['findings'] = lint_conclusion(found['conclusion'], item['conclusion'])
    for finding in record['findings']:
        if 'suggested_edit' in finding:
            finding['witnesses'] = witness_binders(found['binders'], found['conclusion'])
    return dict(record, status='linted')


def lint_candidate(finding):
    edit, witnesses = finding.get('suggested_edit'), finding.get('witnesses')
    if finding['strength'] != 'strong':
        return None, 'only strong findings become claims'
    if not edit:
        return None, 'no unique suggested edit'
    if not witnesses or not witnesses['binders']:
        return None, 'the conclusion uses no theorem binders to quantify over'
    candidate = {'type': 'precedence', 'location': edit['edit_from'],
                 'explanation': 'The binder body parses as (A) ∧ (B) → C, so the implication takes the first conjunct as an assumption, '
                                'and an inner binder shadows the outer binder name. The lint suggests the regrouping (Q, A) ∧ (B → C).',
                 'prediction': 'With the declaration hypotheses dropped, some witnesses satisfy the exact source conclusion but not the regrouped conclusion.',
                 'probe_kind': 'separation', 'comparison': None, 'witnesses': witnesses['binders'],
                 'edit_from': edit['edit_from'], 'edit_to': edit['edit_to'], 'bridge': 'schema',
                 'obligation': 'This claim comes from a deterministic parse lint, not from reading the informal problem. '
                               'A reviewer must check against the informal problem that the regrouped conclusion is the intended reading.'}
    return candidate, None


def lint_claim(item, finding, index):
    candidate, reason = lint_candidate(finding)
    if candidate is None:
        raise ValueError(reason)
    claim = prepare_claim(item, candidate, index)
    claim['id'] = f'{item["id"]}-lint-{index}'
    claim['claim_source'] = 'lint'
    claim['witnesses'] = finding['witnesses']
    claim['transformations'][0] = ('keep the exact source conclusion; replace the declaration binders and hypotheses '
                                   'with the theorem binders the conclusion uses')
    return claim


def audit_lints(worker, client, item, config, directory):
    from yamalemma.pipeline import prove_claim
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    start_calls = len(client.calls) if client else 0
    result = {'item_id': item['id'], 'item_fingerprint': item.get('fingerprint'), 'claim_source': 'lint',
              'claims': [], 'rejected_candidates': [], 'finding_status': 'unconfirmed',
              'proof_stage': 'enabled' if client else 'elaboration_only'}
    if item.get('unsupported') or 'expected_type' not in item:
        result['status'] = 'unsupported_source'
    else:
        validate_item(item, worker.project)
        lint = lint_item(worker, item)
        result['lint'] = lint
        result['status'] = lint['status']
        binding = {'item': item['fingerprint'], 'environment': environment_record(worker.project)['fingerprint'],
                   'config': fingerprint(config), 'prompts': PROMPT_VERSION, 'claim_source': 'lint',
                   'implementation': {name: file_hash(Path(__file__).parent / name) for name in ('models.py', 'prompts.py', 'pipeline.py', 'config.py', 'budget.py', 'credentials.py', 'lints.py')}}
        for index, finding in enumerate(lint['findings'], 1):
            try:
                claim = lint_claim(item, finding, index)
            except ValueError as error:
                result['rejected_candidates'].append({'binder': finding['binder'], 'reason': str(error)})
                continue
            rendering = render_target(worker, item, claim['proposition'])
            if rendering.get('status') != 'rendered':
                reason = str(rendering.get('error') or rendering.get('status'))[:1000]
                result['rejected_candidates'].append({'binder': finding['binder'], 'claim': claim,
                                                      'reason': f'target does not elaborate: {reason}'})
                continue
            claim_directory = directory / f'lint-claim-{index:02d}'
            if client:
                evidence, calls, verdict = prove_claim(worker, client, item, claim, binding, claim_directory, config['limits']['max_repairs'])
            else:
                evidence, calls = [], []
                verdict = adjudicate(claim, [])
                write_report(claim_directory, item, claim, evidence, verdict)
            result['claims'].append({'claim': claim, 'rendered_type': rendering.get('type'), 'adjudication': verdict,
                                     'evidence': evidence, 'model_statuses': [call['status'] for call in calls],
                                     'report_directory': claim_directory.name})
    result['model_calls'] = client.calls[start_calls:] if client else []
    result['elapsed_seconds'] = time.monotonic() - started
    result['new_cost_usd'] = sum(call['new_cost_usd'] for call in result['model_calls'] if call.get('new_cost_usd') is not None)
    result['hash'] = fingerprint(result)
    save_json(directory / 'lint-audit.json', result)
    lines = [f'# Lint audit: {item["id"]}', '', f'Status: {result["status"]}', f'Proof stage: {result["proof_stage"]}',
             f'Lint claims: {len(result["claims"])}', f'Rejected lint candidates: {len(result["rejected_candidates"])}', '',
             'Lint claims are deterministic suspicions about grouping. They are kept separate from reader claims.', '']
    for row in result['claims']:
        lines.append(f'- [{row["claim"]["id"]}]({row["report_directory"]}/report.md): {row["adjudication"]["evidence_verdict"]}')
    (directory / 'lint-audit.md').write_text('\n'.join(lines) + '\n')
    return result


def run_lint_audit(worker, items, config, output, client=None):
    import fcntl
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    with (output / '.run.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ValueError('another audit is already using this output directory') from error
        rows = []
        for index, item in enumerate(items):
            directory = output / 'items' / f'{index:04d}-{fingerprint(item)[:12]}'
            row = audit_lints(worker, client, item, config, directory)
            rows.append({'item_id': item['id'], 'item_fingerprint': item.get('fingerprint'), 'status': row['status'],
                         'claims': [(claim['claim']['id'], claim['adjudication']['evidence_verdict']) for claim in row['claims']],
                         'rejected': len(row['rejected_candidates']), 'report': str(directory / 'lint-audit.json'), 'hash': row['hash']})
            save_json(output / 'summary.json', rows)
            print(f'{item["id"]}: {row["status"]}', flush=True)
        return rows
