"""Run unit, seed and HTTP checks using temporary databases; never touch user data."""
import argparse
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--python-project-1', default=str(ROOT / 'code-smells-project/.venv/bin/python'))
parser.add_argument('--python-project-3', default=str(ROOT / 'task-manager-api/.venv/bin/python'))
parser.add_argument('--node', default=shutil.which('node') or 'node')
parser.add_argument('--output-dir', type=Path, default=ROOT / 'evidence/final-validation')
parser.add_argument('--flask-in-process', action='store_true', help='Use Flask test clients; Express still requires loopback.')
args = parser.parse_args()
output = args.output_dir.resolve()
output.mkdir(parents=True, exist_ok=True)
summary = {'unit': [], 'seed': [], 'http': [], 'status': 'running'}
base_env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'APP_DEBUG': 'false', 'HOST': '127.0.0.1'}


def run(command, project, log_name, env=None, expected=0):
    result = subprocess.run(command, cwd=ROOT / project, env=env or base_env, capture_output=True, text=True, timeout=120)
    (output / log_name).write_text(result.stdout + result.stderr)
    if result.returncode != expected:
        raise RuntimeError(f'{log_name}: exit {result.returncode}, expected {expected}; inspect {output / log_name}')
    return result


def free_port():
    with socket.socket() as listener:
        listener.bind(('127.0.0.1', 0))
        return listener.getsockname()[1]


def wait_ready(process, url):
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError('Application exited before HTTP became ready; inspect server log')
        try:
            with urllib.request.urlopen(url, timeout=1):
                return
        except urllib.error.HTTPError:
            return
        except (urllib.error.URLError, ConnectionError, TimeoutError):
            time.sleep(.1)
    raise RuntimeError('Application did not become ready within 20 seconds')


try:
    with tempfile.TemporaryDirectory(prefix='mvc-validation-') as directory:
        temporary = Path(directory)
        projects = {1: ('code-smells-project', args.python_project_1), 2: ('ecommerce-api-legacy', args.node), 3: ('task-manager-api', args.python_project_3)}
        for number, (project, runtime) in projects.items():
            command = [runtime, '--test', 'tests/architecture.test.js'] if number == 2 else [runtime, '-m', 'unittest', 'discover', '-s', 'tests', '-v']
            run(command, project, f'unit-project-{number}.log')
            summary['unit'].append({'project': number, 'passed': True, 'log': f'unit-project-{number}.log'})
        seed_env = {**base_env, 'DATABASE_URL': 'sqlite:///' + str(temporary / 'seed.db')}
        seed_env.pop('DEMO_PASSWORD', None)
        result = run([args.python_project_3, 'seed.py'], 'task-manager-api', 'seed-missing-password.log', seed_env, expected=1)
        assert 'Set DEMO_PASSWORD' in result.stderr
        seed_env['DEMO_PASSWORD'] = 'local-fixture-only'
        run([args.python_project_3, 'seed.py'], 'task-manager-api', 'seed-first.log', seed_env)
        result = run([args.python_project_3, 'seed.py'], 'task-manager-api', 'seed-existing.log', seed_env, expected=1)
        assert 'Database is not empty' in result.stderr
        verify = "from app import app; from database import db; from models.user import User; from models.category import Category; from models.task import Task; from sqlalchemy import select,func; ctx=app.app_context(); ctx.push(); assert [db.session.scalar(select(func.count()).select_from(m)) for m in (User,Category,Task)]==[1,1,1]; assert db.session.scalar(select(User)).check_password('local-fixture-only'); print('Seed counts and password verified: 1 user, 1 category, 1 task')"
        run([args.python_project_3, '-c', verify], 'task-manager-api', 'seed-integrity.log', seed_env)
        category_env = {**seed_env, 'DATABASE_URL': 'sqlite:///' + str(temporary / 'category-only.db')}
        prepare = "from app import app; from database import db; from models.category import Category; ctx=app.app_context(); ctx.push(); db.session.add(Category(name='Existing')); db.session.commit()"
        run([args.python_project_3, '-c', prepare], 'task-manager-api', 'seed-category-prepare.log', category_env)
        result = run([args.python_project_3, 'seed.py'], 'task-manager-api', 'seed-category-existing.log', category_env, expected=1)
        assert 'Database is not empty' in result.stderr
        verify_category = "from app import app; from database import db; from models.user import User; from models.category import Category; from models.task import Task; from sqlalchemy import select,func; ctx=app.app_context(); ctx.push(); assert [db.session.scalar(select(func.count()).select_from(m)) for m in (User,Category,Task)]==[0,1,0]; assert db.session.scalar(select(Category)).name=='Existing'; print('Existing category unchanged; no seed rows inserted')"
        run([args.python_project_3, '-c', verify_category], 'task-manager-api', 'seed-category-integrity.log', category_env)
        summary['seed'] = [{'case': name, 'passed': True} for name in ('password required', 'initial population', 'repeat refuses without changes', 'password hash verifies', 'category-only database refuses without changes')]
        for number, (project, runtime) in projects.items():
            database = temporary / f'http-project-{number}.db'
            env = {**base_env, 'DATABASE_PATH': str(database), 'DATABASE_URL': 'sqlite:///' + str(database), 'ADMIN_TOKEN': 'temporary-admin-fixture', 'TEST_ADMIN_TOKEN': 'temporary-admin-fixture'}
            in_process = args.flask_in_process and number != 2
            port = 0 if in_process else free_port()
            url = f'http://127.0.0.1:{port}'
            env['PORT'] = str(port)
            process = None
            try:
                if not in_process:
                    server_log = (output / f'server-project-{number}.log').open('w')
                    command = [runtime, 'src/server.js'] if number == 2 else [runtime, 'app.py']
                    process = subprocess.Popen(command, cwd=ROOT / project, env=env, stdout=server_log, stderr=subprocess.STDOUT)
                    wait_ready(process, url)
                command = [args.python_project_1 if number == 2 else runtime, str(ROOT / 'scripts/smoke_http.py'), str(number), url, '--refactored', '--output', str(output / f'http-project-{number}.json')]
                if in_process:
                    command += ['--flask-root', str(ROOT / project)]
                run(command, project, f'http-run-project-{number}.log', env)
                result = json.loads((output / f'http-project-{number}.json').read_text())
                summary['http'].append({key: result[key] for key in ('project', 'transport', 'passed', 'failed', 'checks_passed', 'checks_failed')})
            finally:
                if process is not None:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait(timeout=5)
                    server_log.close()
    summary['status'] = 'passed'
except Exception as error:
    summary['status'] = 'failed'
    summary['error'] = str(error)
    raise
finally:
    (output / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary))
