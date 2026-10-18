import datetime
import hashlib
import json
import subprocess
from pathlib import Path


SKIPPED_SUBJECTS = ('toolchain', 'mathlib', 'bump', 'update to lean', 'update lean', 'merge')


def git(root, *arguments):
    result = subprocess.run(['git', '-C', str(root), *arguments], capture_output=True, text=True)
    if result.returncode != 0:
        raise ValueError(f'git {arguments[0]} failed: {result.stderr.strip()}')
    return result.stdout


def pinned_revision(root):
    commit = git(root, 'rev-parse', 'HEAD').strip()
    if git(root, 'status', '--porcelain', '--', '.').strip():
        raise ValueError('benchmark checkout has local changes; selection needs a clean pinned revision')
    return commit


def find_toolchain(root):
    for directory in (root, *root.parents):
        if (directory / 'lean-toolchain').exists():
            return (directory / 'lean-toolchain').read_text().strip()
        if (directory / '.git').exists():
            break
    return None


def rank(seed, name):
    return hashlib.sha256(f'{seed}:{name}'.encode()).hexdigest()


def select_heldout(root, development, size, seed):
    root = Path(root).resolve()
    if size < 1:
        raise ValueError('selection size must be positive')
    if not seed:
        raise ValueError('selection needs an explicit seed')
    commit = pinned_revision(root)
    files = {path.stem: path for path in sorted(root.glob('*.lean'))}
    if not files:
        raise ValueError('no Lean problem files found in the benchmark source directory')
    development = set(development)
    excluded = sorted(name for name in files if name in development)
    pool = sorted(name for name in files if name not in development)
    if size > len(pool):
        raise ValueError('selection size exceeds the eligible pool')
    chosen = sorted(sorted(pool, key=lambda name: rank(seed, name))[:size])
    return {'schema_version': 1, 'kind': 'yamalemma-heldout-selection',
            'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
            'benchmark_commit': commit, 'toolchain': find_toolchain(root), 'source_directory': root.name,
            'seed': seed, 'size': size, 'pool_size': len(pool), 'development_excluded': excluded,
            'unknown_development_names': sorted(development - set(files)),
            'selected': chosen, 'groups': {name: name for name in chosen},
            'file_sha256': {name: hashlib.sha256(files[name].read_bytes()).hexdigest() for name in chosen},
            'method': 'sha256(seed:name) order over problems outside the development list; one provenance group per problem',
            'caveat': 'public benchmark text and earlier manual audits may have exposed these problems; held-out means unused for development'}


def fix_history(root, since=None):
    root = Path(root).resolve()
    arguments = ['log', '--format=@@%H|%ad|%s', '--date=short', '--name-only']
    if since:
        arguments.append(f'--since={since}')
    rows = []
    for block in git(root, *arguments, '--', '.').split('@@')[1:]:
        lines = [line for line in block.strip().splitlines() if line]
        commit, date, subject = lines[0].split('|', 2)
        problems = sorted({Path(line).stem for line in lines[1:] if line.endswith('.lean')})
        if problems and not any(word in subject.lower() for word in SKIPPED_SUBJECTS):
            rows.append({'commit': commit, 'date': date, 'subject': subject, 'problems': problems})
    return rows


def write_selection(selection, destination):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('x') as stream:
        stream.write(json.dumps(selection, ensure_ascii=False, indent=2) + '\n')


def check_selection(selection, root):
    root = Path(root).resolve()
    if pinned_revision(root) != selection['benchmark_commit']:
        raise ValueError('benchmark checkout is not at the selected revision')
    for name, digest in selection['file_sha256'].items():
        path = root / f'{name}.lean'
        if not path.exists() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f'selected file {name} differs from the selection record')
    return set(selection['selected'])


FIX_WORDS = ('fix', 'correct', 'wrong')
NON_STATEMENT_WORDS = ('fix build', 'deprecation', 'warning', 'syntax highlighting')


def show(root, revision, path):
    try:
        return git(root, 'show', f'{revision}:{path}')
    except ValueError:
        return None


def fix_pairs(root, destination, since=None, exclude=()):
    root = Path(root).resolve()
    commit = pinned_revision(root)
    prefix = git(root, 'rev-parse', '--show-prefix').strip()
    destination = Path(destination)
    (destination / 'sources').mkdir(parents=True, exist_ok=False)
    exclude = set(exclude)
    pairs, skipped = [], []
    for row in fix_history(root, since):
        subject = row['subject'].lower()
        for name in row['problems']:
            group = f'{name}@{row["commit"][:12]}'
            if name in exclude:
                skipped.append({'group': group, 'reason': 'excluded problem'})
                continue
            before = show(root, f'{row["commit"]}^', f'{prefix}{name}.lean')
            after = show(root, row['commit'], f'{prefix}{name}.lean')
            if before is None or after is None:
                skipped.append({'group': group, 'reason': 'file added or removed by this commit'})
                continue
            if before == after:
                skipped.append({'group': group, 'reason': 'file unchanged'})
                continue
            paths = {}
            for role, content in (('pre_fix', before), ('post_fix', after)):
                path = destination / 'sources' / f'{group}-{role}.lean'
                path.write_text(content)
                paths[role] = {'path': str(path.relative_to(destination)), 'sha256': hashlib.sha256(content.encode()).hexdigest()}
            pairs.append({'group': group, 'problem': name, 'commit': row['commit'], 'date': row['date'], 'subject': row['subject'],
                          'fix_like': any(word in subject for word in FIX_WORDS) and not any(word in subject for word in NON_STATEMENT_WORDS),
                          'files': paths})
    manifest = {'schema_version': 1, 'kind': 'yamalemma-fix-pairs', 'benchmark_commit': commit, 'source_directory': prefix,
                'since': since, 'excluded_problems': sorted(exclude), 'pairs': pairs, 'skipped': skipped,
                'caveat': 'a maintainer change is evidence for review, not a label; both versions still need independent review'}
    (destination / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
    return manifest


def ingest_fix_pairs(worker, manifest, directory, informal=None, answers=False):
    from yamalemma.domain import fingerprint
    from yamalemma.harness import render_target
    from yamalemma.ingest import ingest_source
    directory = Path(directory)
    informal = informal or {}
    items, rows = [], []
    for pair in manifest['pairs']:
        row = {'group': pair['group'], 'problem': pair['problem'], 'fix_like': pair['fix_like']}
        for role, record in pair['files'].items():
            path = directory / record['path']
            if hashlib.sha256(path.read_bytes()).hexdigest() != record['sha256']:
                raise ValueError(f'{record["path"]} differs from the fix-pair manifest')
            try:
                found = [item for item in ingest_source(worker, path, origin=f'{pair["commit"]}:{pair["problem"]}.lean ({role})',
                                                        informal=informal.get(pair['problem']), answers=answers)
                         if item['id'] == pair['problem']]
            except ValueError as error:
                row[role] = {'status': 'unparsed', 'reason': str(error)[:300]}
                continue
            if not found:
                row[role] = {'status': 'theorem_not_found'}
                continue
            item = found[0]
            item.update(id=f'{pair["group"]}-{role}', stratum='fix_history', group=pair['group'], role=role,
                        benchmark_commit=pair['commit'] if role == 'post_fix' else f'{pair["commit"]}^')
            item['fingerprint'] = fingerprint({key: value for key, value in item.items() if key != 'fingerprint'})
            items.append(item)
            if item['unsupported']:
                row[role] = {'status': 'unsupported', 'reason': '; '.join(item['unsupported'])[:300]}
                continue
            rendering = render_target(worker, item, item['expected_type'])
            row[role] = {'status': 'elaborates' if rendering.get('status') == 'rendered' else 'does_not_elaborate',
                         'expected_type': item['expected_type']}
            if rendering.get('status') != 'rendered':
                row[role]['reason'] = str(rendering.get('error') or rendering.get('status'))[:300]
        types = [row.get(role, {}).get('expected_type') for role in ('pre_fix', 'post_fix')]
        row['statement_changed'] = None if None in types else types[0] != types[1]
        for role in ('pre_fix', 'post_fix'):
            row.get(role, {}).pop('expected_type', None)
        rows.append(row)
    return items, rows
