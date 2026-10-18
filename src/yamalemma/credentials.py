import os
import stat
from pathlib import Path


KEY_FILE = Path.home() / '.config/yamalemma/openai-api-key'


def load_key(name='OPENAI_API_KEY'):
    value = os.environ.get(name)
    if value:
        return value
    if name != 'OPENAI_API_KEY' or not KEY_FILE.exists():
        return None
    metadata = KEY_FILE.lstat()
    if not stat.S_ISREG(metadata.st_mode) or metadata.st_mode & 0o077 or metadata.st_uid != os.getuid():
        raise ValueError('API key file must be a private regular file owned by the current user (mode 600)')
    if metadata.st_size > 8192:
        raise ValueError('API key file is too large')
    value = KEY_FILE.read_text().strip()
    if not value or any(character.isspace() for character in value):
        raise ValueError('API key file must contain one nonempty key')
    return value
