from yamalemma.domain import fingerprint, validate_claim


def adjudicate(claim, evidence, reviews=()):
    validate_claim(claim)
    claim_id = fingerprint(claim)
    accepted = []
    for entry in evidence:
        if entry.get('claim_fingerprint') != claim_id:
            raise ValueError('evidence belongs to a different formal claim')
        if entry.get('item_fingerprint') != claim['item_fingerprint']:
            raise ValueError('evidence belongs to a different source item')
        if entry.get('accepted'):
            polarity = entry.get('polarity')
            expected = claim['proposition'] if polarity == 'confirm' else f"Not ({claim['proposition']})"
            if polarity not in ('confirm', 'refute') or entry.get('expected') != expected:
                raise ValueError('evidence does not check the claimed polarity')
            if entry.get('type_matches') is not True or entry.get('axiom_policy') != 'allowed':
                raise ValueError('incomplete evidence validation')
            accepted.append(entry)
    polarities = {entry['polarity'] for entry in accepted}
    if len(polarities) == 2:
        verdict = 'INTERNAL-ERROR'
    elif polarities == {'confirm'}:
        verdict = 'EVIDENCE-CHECKED'
    elif polarities == {'refute'}:
        verdict = 'REFUTED'
    else:
        verdict = 'UNRESOLVED'
    obligations = []
    for bridge in claim['bridges']:
        matches = [review for review in reviews
                   if review.get('claim_fingerprint') == claim_id
                   and review.get('obligation') == bridge['obligation']
                   and review.get('method') == 'human'
                   and review.get('reviewer') and review.get('justification')]
        obligations.append(dict(bridge, discharged=bool(matches), reviews=matches))
    confirmed = verdict == 'EVIDENCE-CHECKED' and all(b['discharged'] for b in obligations)
    return {
        'schema_version': 1, 'claim_id': claim['id'], 'claim_fingerprint': claim_id,
        'evidence_verdict': verdict, 'finding_status': 'confirmed' if confirmed else 'unconfirmed',
        'scope': claim['scope'], 'bridges': obligations,
        'evidence_ids': [entry['id'] for entry in accepted],
        'reasons': [entry.get('reason', '') for entry in evidence if not entry.get('accepted')],
    }
