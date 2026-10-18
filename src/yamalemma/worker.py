import json
import math
import os
import selectors
import shutil
import signal
import subprocess
import time
import uuid
from pathlib import Path


class WorkerError(RuntimeError):
    pass


def lake_path():
    return shutil.which('lake') or str(Path.home() / '.elan/bin/lake')


class LeanWorker:
    def __init__(self, project, timeout=60, memory_mb=65536):
        if not math.isfinite(timeout) or timeout <= 0:
            raise ValueError('timeout must be finite and positive')
        if not isinstance(memory_mb, int) or not 1024 <= memory_mb <= 65536:
            raise ValueError('virtual memory allowance must be between 1024 and 65536 MiB')
        self.project = Path(project).resolve()
        self.timeout = timeout
        self.memory_mb = memory_mb
        self.process = None
        self.buffer = b''
        self.generation = 0
        self.checks = 0
        self.command = []

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.close()

    def start(self):
        if self.process is not None:
            return
        if not shutil.which('bwrap') or not shutil.which('prlimit'):
            raise WorkerError('bubblewrap and prlimit are required; no unrestricted fallback')
        lake = lake_path()
        prefix = subprocess.check_output([lake, 'env', 'lean', '--print-prefix'], cwd=self.project, text=True).strip()
        lean_path = subprocess.check_output([lake, 'env', 'printenv', 'LEAN_PATH'], cwd=self.project, text=True).strip()
        paths = [str((self.project / p).resolve()) for p in lean_path.split(':') if p]
        bridge = self.project / 'Yamalemma/Worker.lean'
        command = ['bwrap', '--unshare-all', '--die-with-parent', '--new-session', '--cap-drop', 'ALL',
                   '--ro-bind', '/usr', '/usr', '--symlink', 'usr/lib', '/lib', '--symlink', 'usr/lib64', '/lib64',
                   '--dir', '/etc', '--ro-bind', '/etc/ld.so.cache', '/etc/ld.so.cache',
                   '--proc', '/proc', '--dev', '/dev', '--tmpfs', '/tmp', '--dir', '/work', '--chdir', '/work',
                   '--ro-bind', prefix, prefix, '--ro-bind', str(self.project / '.lake'), str(self.project / '.lake'),
                   '--ro-bind', str(bridge), '/worker/Worker.lean', '--clearenv',
                   '--setenv', 'PATH', f'{prefix}/bin:/usr/bin', '--setenv', 'HOME', '/tmp',
                   '--setenv', 'LEAN_PATH', ':'.join(paths),
                   '--', '/usr/bin/prlimit', f'--as={self.memory_mb * 1024 * 1024}', '--nofile=256', '--fsize=134217728',
                   '--', f'{prefix}/bin/lean', '--run', '/worker/Worker.lean']
        self.command = command
        self.buffer = b''
        self.process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                        stderr=subprocess.PIPE, start_new_session=True)
        self.generation += 1
        try:
            ready = self.read_message(180)
            if ready != {'ready': True, 'protocol': 1}:
                raise WorkerError(f'invalid worker handshake: {ready}')
        except BaseException:
            self.close()
            raise

    def read_message(self, timeout):
        deadline = time.monotonic() + timeout
        stderr = bytearray()
        with selectors.DefaultSelector() as selector:
            selector.register(self.process.stdout, selectors.EVENT_READ, 'stdout')
            selector.register(self.process.stderr, selectors.EVENT_READ, 'stderr')
            while True:
                if b'\n' in self.buffer:
                    line, self.buffer = self.buffer.split(b'\n', 1)
                    try:
                        return json.loads(line)
                    except (ValueError, UnicodeError) as error:
                        raise WorkerError('invalid worker protocol output') from error
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise TimeoutError('Lean worker exceeded its time budget')
                events = selector.select(remaining)
                for key, _ in events:
                    data = os.read(key.fileobj.fileno(), 65536)
                    if not data:
                        selector.unregister(key.fileobj)
                        if key.data == 'stdout':
                            raise WorkerError(f'worker stopped: {stderr.decode(errors="replace")}')
                    elif key.data == 'stdout':
                        self.buffer += data
                    else:
                        stderr.extend(data)
                    if len(self.buffer) + len(stderr) > 8 * 1024 * 1024:
                        raise WorkerError('worker output limit exceeded')

    def request(self, payload, timeout=None):
        budget = self.timeout if timeout is None else timeout
        if not math.isfinite(budget) or budget <= 0:
            raise ValueError('timeout must be finite and positive')
        heartbeats = payload.get('heartbeats', 400000)
        if not isinstance(heartbeats, int) or not 1 <= heartbeats <= 1000000:
            raise ValueError('heartbeat budget must be between 1 and 1000000')
        self.start()
        request = dict(payload, id=uuid.uuid4().hex)
        encoded = (json.dumps(request, ensure_ascii=False) + '\n').encode()
        if len(encoded) > 2 * 1024 * 1024:
            raise ValueError('worker input limit exceeded')
        started = time.monotonic()
        try:
            self.process.stdin.write(encoded)
            self.process.stdin.flush()
            response = self.read_message(budget)
            if 'error' in response:
                result = {'status': 'failure', 'error': response['error']}
            elif response.get('id') != request['id'] or not isinstance(response.get('result'), dict):
                raise WorkerError('worker response identity mismatch')
            else:
                result = response['result']
            self.checks += 1
            return dict(result, elapsed_seconds=time.monotonic() - started, worker_generation=self.generation)
        except TimeoutError:
            self.close()
            return {'status': 'timeout', 'elapsed_seconds': time.monotonic() - started}
        except BaseException:
            self.close()
            raise

    def close(self):
        if self.process is None:
            return
        process, self.process = self.process, None
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.communicate(timeout=10)
        self.buffer = b''
