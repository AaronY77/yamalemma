from yamalemma.domain import require_text


def proposition(template, **slots):
    required = {
        'proposition': ('statement',),
        'vacuity': ('binders',),
        'equivalence': ('statement', 'reading'),
        'separation': ('binders', 'admitted', 'excluded'),
        'expression_equality': ('expression', 'value'),
        'counterexample': ('statement',),
    }
    if template not in required or set(slots) != set(required[template]):
        raise ValueError('unsupported template or incorrect slots')
    for name, value in slots.items():
        require_text(value, name)
    if template == 'proposition':
        return slots['statement']
    if template == 'vacuity':
        return f'∀ {slots["binders"]}, False'
    if template == 'equivalence':
        return f'({slots["statement"]}) ↔ ({slots["reading"]})'
    if template == 'separation':
        return f'∃ {slots["binders"]}, ({slots["admitted"]}) ∧ ¬ ({slots["excluded"]})'
    if template == 'expression_equality':
        return f'({slots["expression"]}) = ({slots["value"]})'
    return f'Not ({slots["statement"]})'
