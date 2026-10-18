import datetime
import json
from pathlib import Path

from yamalemma.domain import fingerprint, load_json, save_json


PACKET_FIELDS = ('id', 'fingerprint', 'origin', 'benchmark_commit', 'snapshot_kind', 'source_sha256', 'span',
                 'declaration_source', 'raw_source', 'docstring', 'informal', 'unsupported',
                 'source_transformations')
PIPELINE_FIELDS = ('claims', 'reader_claims', 'adjudication', 'evidence', 'model_calls', 'no_claim_detected')
LABELS = ('defect', 'control', 'unlabeled')
SPLITS = ('development', 'heldout')
QUESTIONS = [
    'Does the formal statement, including its binders, definitions and answer, express the informal problem?',
    'If not, which mismatch would change the truth value or meaning of the problem?',
    'If an answer was substituted from the benchmark comment, does it match the official solution?',
    'Which official problem source did you compare against?',
]


def check_item(item, split):
    if item.get('status') == 'unsupported' or 'fingerprint' not in item:
        return item.get('reason', 'item was not ingested')
    if fingerprint({key: value for key, value in item.items() if key != 'fingerprint'}) != item['fingerprint']:
        raise ValueError(f'item {item.get("id")} changed after ingestion')
    if any(key in item for key in PIPELINE_FIELDS):
        raise ValueError('review packets must be built from ingested items, not pipeline outputs')
    if split == 'heldout' and not item.get('benchmark_commit'):
        return 'held-out items need a pinned benchmark revision'
    return None


def make_packet(item, split, batch, group=None):
    packet = {'schema_version': 1, 'kind': 'yamalemma-review-packet', 'batch': batch, 'split': split,
              'group': group or item['origin'], 'item': {key: item.get(key) for key in PACKET_FIELDS},
              'questions': QUESTIONS,
              'instructions': 'Review against the official problem source without consulting Yamalemma or model outputs. '
                              'Leave the label empty if you did not complete a review.'}
    packet['fingerprint'] = fingerprint(packet)
    return packet


def response_template(packet):
    return {'packet_fingerprint': packet['fingerprint'], 'item_fingerprint': packet['item']['fingerprint'],
            'item_id': packet['item']['id'], 'group': packet['group'], 'label': None, 'reviewer': '',
            'label_basis': '', 'source_reference': '', 'independent_of_outputs': None}


def export_packets(items, output, split, batch, groups=None):
    if split not in SPLITS:
        raise ValueError('split must be development or heldout')
    if not batch:
        raise ValueError('intake batch needs a name')
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    groups = groups or {}
    entries, excluded, templates, seen = [], [], [], set()
    for index, item in enumerate(items):
        reason = check_item(item, split)
        if reason:
            excluded.append({'id': item.get('id'), 'reason': reason})
            continue
        if item['fingerprint'] in seen:
            raise ValueError('duplicate item in intake batch')
        seen.add(item['fingerprint'])
        packet = make_packet(item, split, batch, groups.get(item['id']))
        path = Path('packets') / f'{index:04d}-{packet["fingerprint"][:12]}.json'
        save_json(output / path, packet)
        entries.append({'id': item['id'], 'item_fingerprint': item['fingerprint'],
                        'packet_fingerprint': packet['fingerprint'], 'path': path.as_posix()})
        templates.append(response_template(packet))
    if not entries:
        raise ValueError('no reviewable items in intake batch')
    manifest = {'schema_version': 1, 'kind': 'yamalemma-intake-manifest', 'batch': batch, 'split': split,
                'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'packets': entries, 'excluded': excluded,
                'note': 'packets contain no labels or pipeline outputs; labels come only from collected reviews'}
    manifest['fingerprint'] = fingerprint(manifest)
    with (output / 'manifest.json').open('x') as stream:
        stream.write(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    save_json(output / 'responses-template.json', templates)
    return manifest


def load_packets(manifest, directory):
    if fingerprint({key: value for key, value in manifest.items() if key != 'fingerprint'}) != manifest.get('fingerprint'):
        raise ValueError('intake manifest changed after export')
    packets = {}
    for entry in manifest['packets']:
        packet = load_json(Path(directory) / entry['path'])
        if fingerprint({key: value for key, value in packet.items() if key != 'fingerprint'}) != entry['packet_fingerprint'] \
                or packet.get('fingerprint') != entry['packet_fingerprint']:
            raise ValueError(f'review packet {entry["path"]} changed after export')
        packets[entry['packet_fingerprint']] = packet
    return packets


def dataset_row(packet, response):
    item = packet['item']
    label = response.get('label') or 'unlabeled'
    if label not in LABELS:
        raise ValueError('label must be defect, control, unlabeled or empty')
    group = response.get('group') or packet['group']
    row = {'item_fingerprint': item['fingerprint'], 'item_id': item['id'], 'label': label,
           'split': packet['split'], 'group': group, 'packet_fingerprint': packet['fingerprint']}
    if label == 'unlabeled':
        return row
    for key in ('reviewer', 'label_basis', 'source_reference'):
        if not isinstance(response.get(key), str) or not response[key].strip():
            raise ValueError(f'labeled response for {item["id"]} needs {key}')
    if response.get('independent_of_outputs') is not True:
        raise ValueError(f'labeled response for {item["id"]} must declare review independent of pipeline outputs')
    row.update(reviewer=response['reviewer'], label_basis=response['label_basis'],
               provenance=f'{response["source_reference"]}; benchmark {item["benchmark_commit"] or "unpinned"}; '
                          f'packet {packet["fingerprint"]}',
               review_attestation='reviewer-declared independent of pipeline outputs; not authenticated')
    return row


def collect_labels(manifest, directory, responses):
    packets = load_packets(manifest, directory)
    answered = {}
    for response in responses:
        key = response.get('packet_fingerprint')
        if key not in packets:
            raise ValueError('response does not match a packet in this batch')
        if key in answered:
            raise ValueError('duplicate response for one packet')
        if response.get('item_fingerprint') != packets[key]['item']['fingerprint']:
            raise ValueError('response item does not match its packet')
        if response.get('split', manifest['split']) != manifest['split']:
            raise ValueError('split is fixed at export and cannot be changed by a response')
        answered[key] = response
    rows = [dataset_row(packets[entry['packet_fingerprint']], answered.get(entry['packet_fingerprint'], {}))
            for entry in manifest['packets']]
    counts = {label: sum(row['label'] == label for row in rows) for label in LABELS}
    return rows, {'batch': manifest['batch'], 'split': manifest['split'], 'manifest_fingerprint': manifest['fingerprint'],
                  'items': len(rows), 'labels': counts, 'unanswered': len(rows) - len(answered),
                  'excluded_at_export': len(manifest['excluded']), 'dataset_fingerprint': fingerprint(rows)}


def write_dataset(rows, destination):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('x') as stream:
        stream.write(json.dumps(rows, ensure_ascii=False, indent=2) + '\n')
