import json
from pathlib import Path

from yamalemma.domain import fingerprint, save_json


class ArtifactStore:
    def __init__(self, root):
        self.root = Path(root)

    def put(self, value):
        key = fingerprint(value)
        path = self.root / 'objects' / f'{key}.json'
        if path.exists():
            if json.loads(path.read_text()) != value:
                raise ValueError('artifact hash collision or corruption')
        else:
            save_json(path, value)
        return key

    def get(self, key):
        if len(key) != 64 or any(c not in '0123456789abcdef' for c in key):
            raise ValueError('invalid artifact identifier')
        value = json.loads((self.root / 'objects' / f'{key}.json').read_text())
        if fingerprint(value) != key:
            raise ValueError('artifact hash mismatch')
        return value

    def event(self, value):
        self.root.mkdir(parents=True, exist_ok=True)
        with (self.root / 'events.jsonl').open('a') as stream:
            stream.write(json.dumps(value, ensure_ascii=False) + '\n')
