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
