import re


GROUPS = ('explicitBinder', 'implicitBinder', 'strictImplicitBinder', 'instBinder')


def walk(node):
    yield node
    for child in node.get('children', []):
        yield from walk(child)


def text(node):
    return (node.get('text') or '').strip()


def find(node, suffix):
    return next((part for part in walk(node) if part['kind'].endswith(suffix)), None)


def identifiers(node):
    names = set()
    for leaf in walk(node):
        if leaf['kind'] == 'ident' and leaf.get('identifier'):
            names |= {leaf['identifier'], leaf['identifier'].split('.')[0]}
    return names


def binder_group(node):
    names = [leaf['identifier'] for leaf in walk(node['children'][1]) if leaf['kind'] == 'ident' and leaf.get('identifier')]
    if node['kind'].endswith('instBinder'):
        typed = node['children'][2]
    else:
        typed = next((child for child in node['children'][2:] if child['kind'] == 'null' and child.get('children')
                      and text(child['children'][0]) == ':'), None)
        typed = typed['children'][-1] if typed else None
    return {'names': names, 'type': text(typed) if typed else None, 'uses': sorted(identifiers(typed)) if typed else [],
            'text': text(node), 'instance': node['kind'].endswith('instBinder')}


def binder_groups(binders):
    return [binder_group(node) for node in binders.get('children', []) if node['kind'].endswith(GROUPS)]


def declaration_signature(worker, item):
    if 'raw_source' not in item or 'span' not in item:
        return {'status': 'unsupported'}
    parsed = worker.request({'action': 'extract', 'source': item['raw_source'].replace('\r\n', '\n')})
    if parsed.get('status') != 'parsed':
        return {'status': 'unparsed', 'error': str(parsed.get('error', parsed.get('status')))[:500]}
    start = item['span']['start_byte']
    for command in parsed['commands']:
        for part in walk(command):
            if part['kind'].endswith('.theorem') and part.get('start') is not None and abs(part['start'] - start) <= 1:
                signature = find(part, '.declSig')
                spec = find(signature['children'][1], '.typeSpec') if signature and len(signature['children']) > 1 else None
                if spec:
                    return {'status': 'found', 'binders': signature['children'][0], 'conclusion': spec['children'][-1]}
    return {'status': 'declaration_not_found'}


def render_binder(group, index):
    kind = re.sub(r'\b(Type|Sort)\*', r'\1', group['type']) if group['type'] else None
    if group['instance'] and not group['names']:
        return f'(_inst{index} : {kind})'
    names = ' '.join(group['names'])
    return f'({names} : {kind})' if kind else f'({names})'


def split_hypotheses(groups, conclusion_names):
    referenced = set(conclusion_names) | {name for group in groups for name in group['uses']}
    hypotheses = [index for index, group in enumerate(groups)
                  if not group['instance'] and group['names'] and group['type'] and not referenced & set(group['names'])]
    witnesses = [index for index in range(len(groups)) if index not in hypotheses]
    return {'witnesses': ' '.join(render_binder(groups[index], index) for index in witnesses),
            'witness_names': [name for index in witnesses for name in groups[index]['names']],
            'hypotheses': [{'names': groups[index]['names'], 'type': groups[index]['type']} for index in hypotheses]}


def hypothesis_signature(worker, item):
    found = declaration_signature(worker, item)
    if found['status'] != 'found':
        return found
    split = split_hypotheses(binder_groups(found['binders']), identifiers(found['conclusion']))
    return dict(split, status='found')
