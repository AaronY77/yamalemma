from yamalemma.domain import save_json


def write_report(directory, item, claim, evidence, verdict):
    directory.mkdir(parents=True, exist_ok=True)
    payload = {'item': item, 'claim': claim, 'evidence': evidence, 'adjudication': verdict}
    save_json(directory / 'report.json', payload)
    lines = [f'# {claim["id"]}', '',
             f'Evidence verdict: **{verdict["evidence_verdict"]}**',
             f'Finding status: **{verdict["finding_status"]}**', '',
             f'Scope: {claim["scope"]}', '', claim['prediction'], '',
             '## Source', '', f'Item fingerprint: `{item["fingerprint"]}`',
             f'Source: {item.get("origin", "local snapshot")}', '',
             '## Formal claim', '', '```lean', claim['proposition'], '```', '',
             '## Bridge obligations', '']
    for bridge in verdict['bridges']:
        lines.append(f'- {bridge["type"]}: {bridge["obligation"]} (discharged: {bridge["discharged"]})')
    lines += ['', '## Evidence', '']
    for entry in evidence:
        lines += [f'- {entry["polarity"]}: {entry["reason"]}',
                  f'  Evidence ID: `{entry["id"]}`',
                  f'  Axioms: {entry.get("axioms", "unavailable")}',
                  f'  Environment: `{entry["environment"]["fingerprint"]}`']
    lines += ['', 'The JSON report contains complete inputs, attempts, and provenance.',
              'Formal evidence does not by itself establish faithfulness to the informal problem.', '']
    (directory / 'report.md').write_text('\n'.join(lines))
    return payload
