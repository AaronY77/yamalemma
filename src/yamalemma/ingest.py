import hashlib
import re
import subprocess
from pathlib import Path

from yamalemma.domain import fingerprint


def walk(node):
    yield node
    for child in node.get('children', []):
        yield from walk(child)


def find(node, suffix):
    return next((part for part in walk(node) if part['kind'].endswith(suffix)), None)


def text(node):
    return node['text'].strip() if node else ''


def source_slice(raw, node):
    if node is None or node['start'] is None or node['end'] is None:
        return ''
    return raw[node['start']:node['end']].decode('utf-8')


def wrap(term, opens):
    result = term
    for opened in reversed(opens):
        result = f'{opened} in\n{result}'
    return result


def declaration_parts(raw, declaration):
    signature = find(declaration, '.declSig') or find(declaration, '.optDeclSig')
    value = find(declaration, '.declValSimple')
    ident = find(declaration, '.declId')
    type_spec = find(signature['children'][1], '.typeSpec') if signature and len(signature['children']) > 1 else None
    if not signature or not value or not type_spec or not ident:
        return None
    name = ident['children'][0].get('identifier') or source_slice(raw, ident).strip()
    binders = source_slice(raw, signature['children'][0]).strip()
    proposition = source_slice(raw, type_spec['children'][-1]).strip()
    proof_node = value['children'][1]
    proof = source_slice(raw, proof_node)
    return name, signature, binders, proposition, proof_node, proof


def proof_binders(raw, signature):
    node = signature['children'][0]
    if node['start'] is None:
        return ''
    result = raw[node['start']:node['end']]
    stars = [part for part in walk(node) if part['kind'] == 'Lean.Elab.Term.«termType*»']
    for part in sorted(stars, key=lambda part: part['start'], reverse=True):
        start, end = part['start'] - node['start'], part['end'] - node['start']
        result = result[:start] + b'_' + result[end:]
    return result.decode()


ANSWER_PLACEHOLDER = re.compile(r'^((?:noncomputable[ \t]+)?(?:abbrev|def)[ \t]+(\S+)[^\n]*:=[ \t]*)sorry([ \t]*\n[ \t]*--[ \t]?([^\n]*))', re.M)


def substitute_answers(source):
    records = []

    def replace(match):
        answer = match.group(4).strip()
        if not answer:
            return match.group(0)
        line = source.count('\n', 0, match.start()) + 1
        records.append({'kind': 'benchmark-answer-comment', 'definition': match.group(2), 'line': line,
                        'original': 'sorry', 'answer': answer,
                        'review': 'reviewer must confirm this answer against the official solution'})
        return f'{match.group(1)}({answer}){match.group(3)}'

    return ANSWER_PLACEHOLDER.sub(replace, source), records


def ingest_source(worker, path, origin=None, informal=None, benchmark_commit=None, answers=False):
    path = Path(path)
    original = path.read_bytes()
    raw, substituted = original, []
    if answers:
        transformed, substituted = substitute_answers(original.decode('utf-8'))
        raw = transformed.encode('utf-8')
    source = raw.decode('utf-8')
    normalized = source.replace('\r\n', '\n')
    parsed = worker.request({'action': 'extract', 'source': normalized})
    if parsed.get('status') != 'parsed':
        raise ValueError(f'Lean could not parse {path.name}: {parsed}')
    if normalized != source:
        offsets = [index for index in range(len(raw)) if raw[max(0, index - 1):index + 1] != b'\r\n'] + [len(raw)]
        for tree in [parsed['header'], *parsed['commands']]:
            for part in walk(tree):
                for position in ('start', 'end'):
                    if part[position] is not None:
                        part[position] = offsets[part[position]]
    imports = [node.get('identifier') or text(node) for node in walk(parsed['header']) if node['kind'] == 'ident']
    unsupported = []
    if any(name != 'Mathlib' and not name.startswith('Mathlib.') for name in imports):
        unsupported.append('imports outside the vetted Mathlib baseline')
    opens, declarations, namespaces, items, scopes = [], [], [], [], []
    open_names = {}
    for command in parsed['commands']:
        kind = command['kind']
        if kind.endswith('.open'):
            opens.append(source_slice(raw, command))
            open_names[opens[-1]] = [part['identifier'] for part in walk(command) if part.get('identifier')]
            continue
        if kind.endswith('.namespace'):
            scopes.append((len(opens), len(unsupported), len(namespaces)))
            namespaces.append(command['children'][1].get('identifier') or text(command['children'][1]))
            continue
        if kind.endswith('.section'):
            scopes.append((len(opens), len(unsupported), len(namespaces)))
            continue
        if kind.endswith('.end'):
            if scopes:
                opened, blocked, named = scopes.pop()
                opens, unsupported, namespaces = opens[:opened], unsupported[:blocked], namespaces[:named]
            continue
        if kind.endswith('.set_option'):
            if 'linter.unusedVariables' not in source_slice(raw, command):
                unsupported.append('source set_option requires explicit support')
            continue
        if kind.endswith('.docComment') or 'printAxioms' in kind:
            continue
        if find(command, '.example'):
            continue
        theorem = find(command, '.theorem')
        declaration = theorem or find(command, '.definition') or find(command, '.abbrev')
        if not declaration:
            if not kind.endswith('.moduleDoc'):
                unsupported.append(f'unsupported context command: {kind}')
            continue
        parts = declaration_parts(raw, declaration)
        if not parts:
            unsupported.append('declaration requires a name, explicit type and simple value')
            continue
        short_name, signature, binders, proposition, proof_node, proof = parts
        name = '.'.join(namespaces + [short_name])
        expected = f'∀ {binders}, {proposition}' if binders else proposition
        complete_proof = f'fun {proof_binders(raw, signature)} =>\n{proof}' if binders else proof
        complete_proof = f'@({complete_proof})'
        references = {part.get('identifier') for part in walk(declaration) if part.get('identifier')}
        references.discard(short_name)
        needed = []
        for record in reversed(declarations):
            if record['name'] in references or record['short_name'] in references:
                needed.insert(0, record['support'])
                references.update(record['references'])
        support = {'name': name, 'namespace': '.'.join(namespaces),
                   'type': wrap(expected, opens), 'value': f'@({wrap(complete_proof, opens)})',
                   'scopes': [name for opened in opens for name in open_names[opened]]}
        declarations.append({'name': name, 'short_name': short_name, 'support': support,
                             'references': references})
        if not theorem:
            continue
        doc = find(command, '.docComment')
        reasons = list(unsupported)
        if any('sorry' in support['value'] for support in needed):
            reasons.append('answer or context definition contains an admitted placeholder')
        item = {
            'schema_version': 1, 'id': name, 'origin': origin or str(path.resolve()),
            'benchmark_commit': benchmark_commit, 'snapshot_kind': 'supplied-source',
            'source_sha256': hashlib.sha256(original).hexdigest(), 'raw_source': source,
            'transformed_source_sha256': hashlib.sha256(raw).hexdigest() if substituted else None,
            'source_transformations': substituted,
            'span': {'start_byte': declaration['start'], 'end_byte': declaration['end']},
            'declaration_source': source_slice(raw, declaration),
            'signature_source': source_slice(raw, signature), 'imports': imports,
            'informal': informal, 'docstring': text(doc),
            'binders': binders, 'conclusion': proposition,
            'expected_type': wrap(expected, opens),
            'proof': f'@({wrap(complete_proof, opens)})',
            'context': {'opens': list(opens), 'declarations': needed, 'namespace': '.'.join(namespaces),
                        'scopes': sorted(set(support['scopes'] + [name for entry in needed for name in entry['scopes']]))},
            'proof_syntax': sorted({part['kind'] for part in walk(proof_node)}),
            'transformations': ['close theorem binders; infer proof-binder universe placeholders from the fixed expected type',
                                'recheck referenced supporting declarations in source order',
                                'parse normalized line endings with original UTF-8 byte coordinates']
                               + (['replace admitted answer placeholders with the answer written in the benchmark comment that follows them; byte coordinates refer to the transformed source'] if substituted else []),
            'unsupported': reasons,
            'environment': {'toolchain': (worker.project / 'lean-toolchain').read_text().strip(),
                            'manifest_sha256': hashlib.sha256((worker.project / 'lake-manifest.json').read_bytes()).hexdigest()},
        }
        item['fingerprint'] = fingerprint(item)
        items.append(item)
    return items


def ingest_putnam(worker, root, informal_records=None, benchmark_commit=None, names=None, answers=False):
    root = Path(root).resolve()
    records = informal_records or {}
    git = subprocess.run(['git', '-C', str(root), 'rev-parse', 'HEAD'], capture_output=True, text=True)
    actual_commit = git.stdout.strip() if git.returncode == 0 else None
    if actual_commit:
        changes = subprocess.run(['git', '-C', str(root), 'status', '--porcelain', '--', '.'], capture_output=True, text=True)
        if changes.returncode != 0 or changes.stdout.strip():
            actual_commit = None
    if benchmark_commit is not None and actual_commit != benchmark_commit:
        raise ValueError('supplied benchmark commit does not match the source checkout')
    benchmark_commit = actual_commit
    expected_toolchain = (worker.project / 'lean-toolchain').read_text().strip()
    source_toolchain = None
    for directory in (root, *root.parents):
        if (directory / 'lean-toolchain').exists():
            source_toolchain = (directory / 'lean-toolchain').read_text().strip()
            break
        if (directory / '.git').exists():
            break
    if source_toolchain is not None and source_toolchain != expected_toolchain:
        raise ValueError('benchmark toolchain differs from the worker; create a matching pinned environment')
    output = []
    for path in sorted(root.rglob('*.lean')):
        if '.lake' in path.parts or (names is not None and path.stem not in names):
            continue
        try:
            options = {'origin': str(path.relative_to(root)), 'informal': records.get(path.stem), 'benchmark_commit': benchmark_commit}
            try:
                items = ingest_source(worker, path, answers=answers, **options)
            except ValueError as error:
                if not answers:
                    raise
                items = ingest_source(worker, path, **options)
                for item in items:
                    item['unsupported'].append(f'benchmark answer comment could not be substituted: {str(error)[:200]}')
                    item['fingerprint'] = fingerprint({key: value for key, value in item.items() if key != 'fingerprint'})
            output.extend(items)
        except ValueError as error:
            output.append({'id': path.stem, 'status': 'unsupported', 'reason': str(error),
                           'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    return output
