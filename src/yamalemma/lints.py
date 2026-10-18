from yamalemma.prompts import edit_kind


BINDER_SUFFIXES = ('term∀__,_»', 'term∃__,_»', 'term∃_,_»', 'Term.forall', 'Term.fun', 'term∃!_,_»')
IMPLICATIONS = ('Lean.Parser.Term.arrow', '«term_↔_»')
CONNECTIVES = ('«term_∧_»', '«term_∨_»')


def walk(node):
    yield node
    for child in node.get('children', []):
        yield from walk(child)


def text(node):
    return (node.get('text') or '').strip()


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


def find(node, suffix):
    return next((part for part in walk(node) if part['kind'].endswith(suffix)), None)


def lint_item(worker, item):
    record = {'item_id': item.get('id'), 'item_fingerprint': item.get('fingerprint'), 'findings': [],
              'scope': 'deterministic parse lint; a finding is a suspicion about grouping, not a confirmed defect'}
    if 'raw_source' not in item or 'span' not in item:
        return dict(record, status='unsupported')
    parsed = worker.request({'action': 'extract', 'source': item['raw_source'].replace('\r\n', '\n')})
    if parsed.get('status') != 'parsed':
        return dict(record, status='unparsed', error=str(parsed.get('error', parsed.get('status')))[:500])
    start = item['span']['start_byte']
    for command in parsed['commands']:
        for part in walk(command):
            if part['kind'].endswith('.theorem') and part.get('start') is not None and abs(part['start'] - start) <= 1:
                signature = find(part, '.declSig')
                spec = find(signature['children'][1], '.typeSpec') if signature and len(signature['children']) > 1 else None
                if spec:
                    record['findings'] = lint_conclusion(spec['children'][-1], item['conclusion'])
                    return dict(record, status='linted')
    return dict(record, status='declaration_not_found')
