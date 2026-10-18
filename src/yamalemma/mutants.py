import hashlib
import json
import re
import tempfile
from pathlib import Path

from yamalemma.axiom_policy import assess_axioms
from yamalemma.domain import fingerprint
from yamalemma.harness import render_target
from yamalemma.ingest import ANSWER_PLACEHOLDER, ingest_source, wrap
from yamalemma.signature import binder_groups, find, identifiers, split_hypotheses, walk


OPERATORS = ('precedence', 'scope', 'boundary', 'domain', 'extra_hyp', 'missing_hyp', 'wrong_answer')
COMPARISONS = {'«term_<_»': ('<', '≤'), '«term_≤_»': ('≤', '<'), '«term_>_»': ('>', '≥'), '«term_≥_»': ('≥', '>')}
INTERVALS = {'Icc': 'Ico', 'Ico': 'Icc', 'Ioc': 'Ioo', 'Ioo': 'Ioc', 'Ici': 'Ioi', 'Ioi': 'Ici', 'Iic': 'Iio', 'Iio': 'Iic'}
FORALLS = ('term∀__,_»', 'Term.forall')
EXISTS = ('term∃__,_»', 'term∃_,_»')
NUMBERS = ('ℕ', 'ℤ', 'ℚ', 'ℝ')
EQUIVALENCE_PROOFS = ('Iff.rfl', 'by simp', 'by constructor <;> intro h <;> simpa using h', 'by constructor <;> intro h <;> simp_all')
DIFFERENCE_PROOFS = ('by norm_num', 'by decide', 'by simp')
LINT_CIRCULARITY = ('circular: the precedence operator removes parentheses, and the lint looks for parenthesization patterns; '
                    'lint recall on precedence mutants measures the operator, not the lint, and is not a headline number')


def rank(seed, *parts):
    return hashlib.sha256(':'.join((seed,) + parts).encode()).hexdigest()


def theorem_node(parsed, name):
    for command in parsed['commands']:
        for part in walk(command):
            if part['kind'].endswith('.theorem'):
                ident = find(part, '.declId')
                if ident and ident['children'][0].get('identifier') == name:
                    return part
    return None


def spans(node):
    return node.get('start') is not None and node.get('end') is not None


def edit(start, end, replacement, operator, detail):
    return {'operator': operator, 'start': start, 'end': end, 'replacement': replacement, 'detail': detail}


def boundary_edits(nodes, raw):
    edits = []
    for node in nodes:
        for part in walk(node):
            if part['kind'] in COMPARISONS and len(part['children']) == 3 and spans(part['children'][1]):
                token = part['children'][1]
                before, after = COMPARISONS[part['kind']]
                start = token['start']
                if raw[start:start + len(before.encode())].decode() == before:
                    edits.append(edit(start, start + len(before.encode()), after, 'boundary', f'{before} to {after}'))
    return edits


def domain_edits(nodes, raw):
    edits = []
    for node in nodes:
        for part in walk(node):
            name = part.get('identifier') if part['kind'] == 'ident' else None
            last = name.split('.')[-1] if name else None
            if last in INTERVALS and spans(part):
                text = raw[part['start']:part['end']].decode()
                position = text.rfind(last)
                if position >= 0:
                    start = part['start'] + len(text[:position].encode())
                    edits.append(edit(start, start + len(last.encode()), INTERVALS[last], 'domain', f'{last} to {INTERVALS[last]}'))
    return edits


def precedence_edits(conclusion, raw):
    edits = []
    for part in walk(conclusion):
        for child in part.get('children', []):
            if child['kind'] == 'Lean.Parser.Term.paren' and spans(child) and part is not conclusion and len(part.get('children', [])) >= 2:
                inner = child['children'][1]
                if inner['kind'].startswith('«term_') or inner['kind'] == 'Lean.Parser.Term.arrow':
                    text = raw[child['start']:child['end']].decode()
                    if text.startswith('(') and text.endswith(')'):
                        edits.append(edit(child['start'], child['end'], text[1:-1], 'precedence', f'remove parentheses around {text[:60]}'))
    return edits


def scope_edits(conclusion, raw):
    edits = []
    for part in walk(conclusion):
        outer_kind = 'forall' if part['kind'].endswith(FORALLS) else 'exists' if part['kind'].endswith(EXISTS) else None
        if not outer_kind or not spans(part):
            continue
        body = part['children'][-1]
        inner_kind = 'forall' if body['kind'].endswith(FORALLS) else 'exists' if body['kind'].endswith(EXISTS) else None
        if inner_kind and inner_kind != outer_kind and spans(body) and spans(body['children'][-1]):
            inner_body = body['children'][-1]
            header = raw[part['start']:body['start']].decode()
            inner_header = raw[body['start']:inner_body['start']].decode()
            rest = raw[inner_body['start']:part['end']].decode()
            replacement = f'{inner_header.rstrip()} {header.rstrip()} {rest}'
            edits.append(edit(part['start'], part['end'], replacement, 'scope', f'swap {outer_kind} and {inner_kind}'))
    return edits


def hypothesis_edits(binders, conclusion, raw):
    groups = binder_groups(binders)
    nodes = [node for node in binders.get('children', []) if node['kind'].endswith(('explicitBinder', 'implicitBinder', 'strictImplicitBinder', 'instBinder'))]
    split = split_hypotheses(groups, identifiers(conclusion))
    hypothesis_names = [tuple(row['names']) for row in split['hypotheses']]
    used = identifiers(conclusion)
    all_names = {name for group in groups for name in group['names']}
    hypothesis_text = ' '.join(row['type'] for row in split['hypotheses'])
    edits = []
    for group, node in zip(groups, nodes):
        if tuple(group['names']) in hypothesis_names and spans(node):
            start = node['start']
            while start > 0 and raw[start - 1:start] in (b' ', b'\n', b'\t'):
                start -= 1
            edits.append(edit(start, node['end'], '', 'missing_hyp', f'drop hypothesis {" ".join(group["names"])}'))
        if (not group['instance'] and len(group['names']) == 1 and group['type'] in NUMBERS and group['names'][0] in used and spans(node)):
            name = group['names'][0]
            if re.search(rf'(0 < {re.escape(name)}\b|\b{re.escape(name)} > 0|0 ≤ {re.escape(name)}\b|\b{re.escape(name)} ≥ 0)', hypothesis_text):
                continue
            label = next(candidate for candidate in (f'h{name}pos', f'h{name}0', f'h{name}_pos') if candidate not in all_names)
            edits.append(edit(node['end'], node['end'], f'\n({label} : 0 < {name})', 'extra_hyp', f'add hypothesis 0 < {name}'))
    return edits


def answer_edits(raw):
    text = raw.decode()
    edits = []
    for match in ANSWER_PLACEHOLDER.finditer(text):
        answer_start = match.start(4)
        for number in re.finditer(r'(?<![\w.])\d+(?![\w.])', match.group(4)):
            start = len(text[:answer_start + number.start()].encode())
            value = int(number.group())
            edits.append(edit(start, start + len(number.group().encode()), str(value + 1), 'wrong_answer', f'answer numeral {value} to {value + 1}'))
    return edits


def candidate_edits(worker, raw, name):
    parsed = worker.request({'action': 'extract', 'source': raw.decode()})
    if parsed.get('status') != 'parsed':
        return []
    theorem = theorem_node(parsed, name)
    signature = find(theorem, '.declSig') if theorem else None
    spec = find(signature['children'][1], '.typeSpec') if signature and len(signature['children']) > 1 else None
    if not spec:
        return []
    binders, conclusion = signature['children'][0], spec['children'][-1]
    hypotheses = [node for node in binders.get('children', [])]
    edits = (precedence_edits(conclusion, raw) + scope_edits(conclusion, raw) + boundary_edits([conclusion] + hypotheses, raw)
             + domain_edits([conclusion] + hypotheses, raw) + hypothesis_edits(binders, conclusion, raw) + answer_edits(raw))
    return edits


def apply_edit(raw, change):
    return raw[:change['start']] + change['replacement'].encode() + raw[change['end']:]


def neutral_id(seed, group, role):
    return f'syn-{rank(seed, "id", group, role)[:12]}'


def ingest_neutral(worker, raw, name, item_id, directory, informal=None, commit=None):
    path = Path(directory) / f'{item_id}.lean'
    path.write_bytes(raw)
    try:
        items = [item for item in ingest_source(worker, path, origin=f'{item_id}.lean', informal=informal, benchmark_commit=commit, answers=True)
                 if item['id'] == name]
    except ValueError as error:
        return None, f'unparsed: {str(error)[:200]}'
    if not items:
        return None, 'theorem not found'
    item = items[0]
    if item['unsupported']:
        return None, 'unsupported: ' + '; '.join(item['unsupported'])[:200]
    rendering = render_target(worker, item, item['expected_type'])
    if rendering.get('status') != 'rendered':
        return None, f'does not elaborate: {str(rendering.get("error") or rendering.get("status"))[:200]}'
    item = dict(item, id=item_id)
    item['fingerprint'] = fingerprint({key: value for key, value in item.items() if key != 'fingerprint'})
    return dict(item, rendered=rendering['type']), None


def comparable(item):
    return [item['rendered']] + [[entry['type'], entry['value']] for entry in item['context']['declarations']]


def free_proof(worker, item, proposition, proofs):
    context = item['context']
    allowed = json.loads((Path(__file__).parent / 'proof_syntax.json').read_text())
    for proof in proofs:
        response = worker.request({'expected': proposition, 'proof': proof, 'allowed_syntax': allowed,
                                   'context': context['declarations'], 'namespace': context['namespace'], 'scopes': context.get('scopes', [])})
        axioms = response.get('axioms')
        if response.get('status') == 'checked' and response.get('type_matches') and isinstance(axioms, list) \
                and assess_axioms(tuple(axioms)).status == 'allowed':
            return proof
    return None


def answer_values(item):
    return [(record['definition'], record['answer']) for record in item.get('source_transformations', [])]


def equivalence_bucket(worker, original, mutant, operator):
    if operator == 'wrong_answer':
        values = dict(answer_values(original))
        changed = [(name, values.get(name), answer) for name, answer in answer_values(mutant) if values.get(name) != answer]
        if len(changed) != 1:
            return 'undetermined', None, 'answer change not isolated'
        name, before, after = changed[0]
        support = next(entry for entry in original['context']['declarations'] if entry['name'].endswith(name))
        kind = re.sub(r'^(open [^\n]* in\n)+', '', support['type'])
        opens = original['context']['opens']
        proof = free_proof(worker, original, wrap(f'(({before}) : {kind}) ≠ (({after}) : {kind})', opens), DIFFERENCE_PROOFS)
        if proof:
            return 'proved_different', proof, 'the substituted answer values are distinct'
        same = free_proof(worker, original, wrap(f'(({before}) : {kind}) = (({after}) : {kind})', opens), DIFFERENCE_PROOFS)
        if same:
            return 'proved_equivalent', same, 'the substituted answer values are equal'
        return 'undetermined', None, 'answer values not compared automatically'
    if original['context'] != mutant['context']:
        return 'undetermined', None, 'supporting declarations differ'
    statement = f'({original["expected_type"]}) ↔ ({mutant["expected_type"]})'
    proof = free_proof(worker, original, statement, EQUIVALENCE_PROOFS)
    if proof:
        return 'proved_equivalent', proof, 'original and mutant proved logically equivalent'
    return 'undetermined', None, 'no free equivalence or difference proof found'


def generate(worker, root, names, seed, originals, informal, commit, operators=OPERATORS, skip=()):
    root = Path(root)
    pool = sorted((name for name in names if name not in set(skip)), key=lambda name: rank(seed, name))
    quota = {operator: 0 for operator in operators}
    rows, rejected = [], []
    with tempfile.TemporaryDirectory() as directory:
        for name in pool:
            if len(rows) >= originals:
                break
            raw = (root / f'{name}.lean').read_bytes().replace(b'\r\n', b'\n')
            edits = candidate_edits(worker, raw, name)
            available = {change['operator'] for change in edits}
            order = sorted((operator for operator in operators if operator in available), key=lambda operator: (quota[operator], operators.index(operator)))
            if not order:
                rejected.append({'problem': name, 'reason': 'no applicable operator'})
                continue
            original, reason = ingest_neutral(worker, raw, name, neutral_id(seed, name, 'original'), directory, informal.get(name), commit)
            if original is None:
                rejected.append({'problem': name, 'reason': f'original {reason}'})
                continue
            accepted = None
            for operator in order:
                choices = sorted((change for change in edits if change['operator'] == operator),
                                 key=lambda change: rank(seed, name, operator, str(change['start'])))
                for change in choices[:4]:
                    mutant, reason = ingest_neutral(worker, apply_edit(raw, change), name, neutral_id(seed, name, 'mutant'), directory,
                                                    informal.get(name), commit)
                    if mutant is None:
                        rejected.append({'problem': name, 'operator': operator, 'reason': f'mutant {reason}'})
                        continue
                    if comparable(mutant) == comparable(original):
                        rejected.append({'problem': name, 'operator': operator, 'reason': 'mutant renders identically to the original'})
                        continue
                    accepted = (change, mutant)
                    break
                if accepted:
                    break
            if not accepted:
                continue
            change, mutant = accepted
            quota[change['operator']] += 1
            bucket, proof, basis = equivalence_bucket(worker, original, mutant, change['operator'])
            rows.append({'group': name, 'original': original, 'mutant': mutant, 'mutation': change,
                         'equivalence': {'bucket': bucket, 'proof': proof, 'basis': basis}})
    return rows, rejected, quota


def strip(item):
    return {key: value for key, value in item.items() if key != 'rendered'}


def blinded_outputs(rows, seed, commit, file_hashes):
    items, key, dataset = [], [], []
    for row in rows:
        for role in ('original', 'mutant'):
            item = strip(row[role])
            items.append(item)
            label = 'control' if role == 'original' else 'defect'
            mutation = row['mutation'] if role == 'mutant' else None
            key.append({'item_id': item['id'], 'item_fingerprint': item['fingerprint'], 'group': row['group'], 'role': role,
                        'operator': mutation['operator'] if mutation else None, 'mutation': mutation,
                        'equivalence': row['equivalence'] if role == 'mutant' else None,
                        'signature_source': item['signature_source']})
            dataset.append({'item_fingerprint': item['fingerprint'], 'item_id': item['id'], 'label': label, 'split': 'synthetic',
                            'group': row['group'], 'synthetic': True,
                            'construction': 'yamalemma mutate: one parse-tree edit to the benchmark file, then the standard ingest with answer substitution',
                            'label_basis': (f'synthetic defect by construction ({mutation["operator"]}: {mutation["detail"]}); equivalence bucket {row["equivalence"]["bucket"]}'
                                            if mutation else 'synthetic control: unmodified benchmark statement; not an independent faithfulness review'),
                            'provenance': f'PutnamBench {commit} {row["group"]}.lean sha256 {file_hashes.get(row["group"])}'})
    order = sorted(range(len(items)), key=lambda index: rank(seed, 'order', items[index]['id']))
    return [items[index] for index in order], sorted(key, key=lambda row: row['item_id']), [dataset[index] for index in order]


def wilson(successes, total, z=1.96):
    if not total:
        return None
    phat = successes / total
    denominator = 1 + z * z / total
    centre = (phat + z * z / (2 * total)) / denominator
    margin = z * ((phat * (1 - phat) / total + z * z / (4 * total * total)) ** 0.5) / denominator
    return [round(max(0.0, centre - margin), 3), round(min(1.0, centre + margin), 3)]


def rate(hits, total):
    return {'hits': hits, 'n': total, 'rate': round(hits / total, 3) if total else None, 'wilson95': wilson(hits, total)}


def site(row):
    mutation = row['mutation']
    return mutation['replacement'].strip() if mutation else None


def located(claim, row):
    if row['operator'] == 'wrong_answer':
        return claim['type'] == 'wrong_answer' or '_solution' in claim['location']
    if row['operator'] == 'missing_hyp':
        return claim['type'] in ('missing_hyp', 'extra_hyp', 'domain')
    text = site(row)
    location = claim['location']
    return bool(text) and (text in location or location in text or any(token in location for token in re.findall(r'\S{3,}', text)[:3]))


def lint_flag(record):
    return bool(record and record.get('findings'))


def score_mutants(key, arms, lint):
    rows = {row['item_fingerprint']: row for row in key}
    result = {'scope': 'synthetic mutants and their unmodified originals; detection of planted defects, not recall on real benchmark defects',
              'items': len(rows), 'arms': {}}
    buckets = ('proved_different', 'undetermined', 'proved_equivalent')
    for arm, reports in arms.items():
        by_item = {report['item_fingerprint']: report for report in reports}
        table = {}
        for level in ('reader_suspicion', 'reader_suspicion_located', 'evidence_checked', 'evidence_checked_located'):
            def hit(report, row):
                if report is None:
                    return False
                if level.startswith('reader'):
                    claims = report['reader_claims']
                    return bool(claims) if level == 'reader_suspicion' or row['role'] == 'original' else any(located(claim, row) for claim in claims)
                checked = [entry['claim'] for entry in report['claims'] if entry['adjudication'].get('evidence_verdict') == 'EVIDENCE-CHECKED']
                return bool(checked) if level == 'evidence_checked' or row['role'] == 'original' else any(located(claim, row) for claim in checked)
            entry = {'false_alarm_on_originals': rate(sum(hit(by_item.get(key), row) for key, row in rows.items() if row['role'] == 'original'),
                                                      sum(row['role'] == 'original' for row in rows.values()))}
            for bucket in buckets:
                members = [(key, row) for key, row in rows.items() if row['role'] == 'mutant' and row['equivalence']['bucket'] == bucket]
                entry[f'detection_{bucket}'] = rate(sum(hit(by_item.get(key), row) for key, row in members), len(members))
            operators = {}
            for operator in OPERATORS:
                members = [(key, row) for key, row in rows.items() if row['role'] == 'mutant' and row['operator'] == operator]
                if members:
                    operators[operator] = rate(sum(hit(by_item.get(key), row) for key, row in members), len(members))
            entry['detection_by_operator'] = operators
            table[level] = entry
        claims = [entry for report in reports for entry in report['claims']]
        table['run'] = {'reports': len(by_item), 'missing': len(rows.keys() - by_item.keys()),
                        'formal_claims': len(claims),
                        'evidence_checked': sum(entry['adjudication'].get('evidence_verdict') == 'EVIDENCE-CHECKED' for entry in claims),
                        'unresolved': sum(entry['adjudication'].get('evidence_verdict') == 'UNRESOLVED' for entry in claims),
                        'rejected_candidates': sum(len(report.get('rejected_candidates', [])) for report in reports),
                        'model_calls': sum(len(report.get('model_calls', [])) for report in reports),
                        'cost_usd': round(sum(report.get('new_cost_usd', 0) for report in reports), 4),
                        'seconds': round(sum(report.get('elapsed_seconds', 0) for report in reports), 1)}
        result['arms'][arm] = table
    lint_by = {record['item_fingerprint']: record for record in lint}
    lint_table = {'false_alarm_on_originals': rate(sum(lint_flag(lint_by.get(key)) for key, row in rows.items() if row['role'] == 'original'),
                                                   sum(row['role'] == 'original' for row in rows.values()))}
    for operator in OPERATORS:
        members = [key for key, row in rows.items() if row['role'] == 'mutant' and row['operator'] == operator]
        if members:
            lint_table[operator] = rate(sum(lint_flag(lint_by.get(key)) for key in members), len(members))
    if 'precedence' in lint_table:
        lint_table['precedence_note'] = LINT_CIRCULARITY
    result['lint'] = lint_table
    return result
