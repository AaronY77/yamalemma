import json
import os
import signal
import subprocess
import time
import urllib.request
from pathlib import Path


ROOT = Path.home() / '.local/share/yamalemma'
ENDPOINT = 'http://127.0.0.1:11434'


def get_json(path):
    with urllib.request.urlopen(ENDPOINT + path, timeout=5) as response:
        return json.load(response)


def local_model(action):
    if action == 'status':
        try:
            return {'status': 'running', 'version': get_json('/api/version'), 'models': get_json('/api/tags'), 'loaded': get_json('/api/ps')}
        except OSError:
            return {'status': 'stopped', 'installation': str(ROOT / 'installation.json')}
    if action == 'start':
        if local_model('status')['status'] == 'running':
            return local_model('status')
        record = json.loads((ROOT / 'installation.json').read_text())
        executable = (Path(record['install_root']) / 'bin/ollama').resolve()
        if not executable.is_relative_to(ROOT.resolve()) or not executable.is_file():
            raise ValueError('invalid local Ollama installation path')
        env = dict(os.environ, OLLAMA_HOST='127.0.0.1:11434', OLLAMA_MODELS=str(ROOT / 'models'),
                   OLLAMA_CONTEXT_LENGTH='4096', OLLAMA_NUM_PARALLEL='1', OLLAMA_MAX_LOADED_MODELS='1', OLLAMA_NO_CLOUD='1')
        with (ROOT / 'server.log').open('a') as log:
            process = subprocess.Popen([str(executable), 'serve'], env=env, stdout=log, stderr=log,
                                       stdin=subprocess.DEVNULL, start_new_session=True)
        (ROOT / 'server.pid').write_text(str(process.pid))
        for _ in range(60):
            if process.poll() is not None:
                raise RuntimeError('local model server stopped; inspect server.log')
            if local_model('status')['status'] == 'running':
                return local_model('status')
            time.sleep(0.5)
        raise TimeoutError('local model server did not become ready')
    if action == 'stop':
        pid = int((ROOT / 'server.pid').read_text())
        command = Path(f'/proc/{pid}/cmdline')
        if not command.exists():
            return {'status': 'stopped'}
        args = command.read_bytes().split(b'\0')
        executable = Path(args[0].decode()).resolve()
        if not executable.is_relative_to(ROOT.resolve()) or executable.name != 'ollama' or b'serve' not in args:
            raise ValueError('recorded PID does not belong to this project model server')
        os.kill(pid, signal.SIGTERM)
        return {'status': 'stop_requested', 'pid': pid}
    raise ValueError('unknown local model action')
